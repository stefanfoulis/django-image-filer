import os
import mptt
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.files.storage import FileSystemStorage
from django.core.files.base import File, ContentFile
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date
from image_filer.utils import EXIF
from sorl.thumbnail import fields as thumbnail_fields
from image_filer.fields import ImageFilerModelImageField, \
    ImageFilerModelFolderField

from managers import FolderManager
from django.db.models.signals import post_init
from django.utils.functional import curry
from django.core.urlresolvers import reverse
import StringIO


from django.contrib.auth import models as auth_models

from django.conf import settings
from image_filer.utils.pil_exif import get_exif_for_file, set_exif_subject_location
from image_filer import context_processors

IMAGE_FILER_UPLOAD_ROOT = getattr(settings,'IMAGE_FILER_UPLOAD_ROOT', 'catalogue')

from image_filer.models.safe_file_storage import SafeFilenameFileSystemStorage
fs = SafeFilenameFileSystemStorage()

from django.core.exceptions import ImproperlyConfigured
if not 'image_filer.context_processors.media' in settings.TEMPLATE_CONTEXT_PROCESSORS: raise ImproperlyConfigured("image_filer needs 'image_filer.context_processors.media' to be in settings.TEMPLATE_CONTEXT_PROCESSORS")


class AbstractFile(models.Model):
    """
    Represents a "File-ish" thing that is in a Folder. Any subclasses must
    at least define a foreign key to folder and a file field (or subclass thereof):
        path: return the full absolute path to the physical file (may be omited in special cases)
        file: return a file object
    """
    file_type = 'unknown'
    folder = models.ForeignKey("Folder", related_name='%(class)s_files', null=True, blank=True)
    
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    owner = models.ForeignKey(auth_models.User, related_name='owned_%(class)ss', null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        if self.name in ('', None):
            text = u"%s" % (self.original_filename,)
        else:
            text = u"%s" % (self.name,)
        return text
    
    class Meta:
        abstract=True

class Folder(models.Model):
    """
    Represents a Folder that things (files) can be put into. Folders are *NOT*
    mirrored in the Filesystem and can have any unicode chars as their name.
    Other models may attach to a folder with a ForeignKey. If the related name
    ends with "_files" they will automatically be listed in the 
    folder.files list along with all the other models that link to the folder
    in this way. Make sure the linked models obey the AbstractFile interface
    (Duck Type).
    """
    file_type = 'Folder'
    is_root = False
    can_have_subfolders = True
    
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    
    owner = models.ForeignKey(auth_models.User, related_name='owned_folders', null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    objects = FolderManager()
    
    
    def _get_file_relationships(self):
        # TODO: make this a "multi iterator" that can iterate over multiple
        #         querysets without having to load all objects
        rel = []
        for attr in dir(self):
            if not attr.startswith('_') and attr.endswith('_files'):
                # TODO: also check for fieldtype
                rel.append(getattr(self, attr))
        return rel
    
    @property
    def file_count(self):
        c = 0
        rel = self._get_file_relationships()
        for files in rel:
            c += files.count()
        return c
    @property
    def children_count(self):
        return self.children.count()
    @property
    def item_count(self):
        return self.file_count + self.children_count
    @property
    def files(self):
        rel = self._get_file_relationships()
        result = []
        for files in rel:
            for file in files.all():
                result.append(file)
        return result
    
    def has_edit_permission(self, request):
        return self.has_generic_permission(request, 'edit')
    def has_read_permission(self, request):
        return self.has_generic_permission(request, 'read')
    def has_add_children_permission(self, request):
        return self.has_generic_permission(request, 'add_children')
    def has_generic_permission(self, request, type):
        """
        Return true if the current user has permission on this
        folder. Return the string 'ALL' if the user has all rights.
        """
        user = request.user
        if not user.is_authenticated() or not user.is_staff:
            return False
        elif user.is_superuser:
            return True
        elif user == self.owner:
            return True
        else:
            att_name = "permission_%s_cache" % type
            if not hasattr(self, "permission_user_cache") or \
               not hasattr(self, att_name) or \
               request.user.pk != self.permission_user_cache.pk:
                func = getattr(FolderPermission.objects, "get_%s_id_list" % type)
                permission = func(user)
                self.permission_user_cache = request.user
                if permission == "All" or self.id in permission:
                    setattr(self, att_name, True)
                    self.permission_edit_cache = True
                else:
                    setattr(self, att_name, False)
            return getattr(self, att_name)
    
    def __unicode__(self):
        return u"%s" % (self.name,)
    class Meta:
        unique_together = (('parent','name'),)
        ordering = ('name',)
        permissions = (("can_use_directory_listing", "Can use directory listing"),)

# MPTT registration
try:
    mptt.register(Folder)
except mptt.AlreadyRegistered:
    pass


class Image(AbstractFile):
    SIDEBAR_IMAGE_WIDTH = 210
    DEFAULT_THUMBNAILS = {
                        'admin_clipboard_icon': {'size': (32,32), 'options': ['crop','upscale']},
                        'admin_sidebar_preview': {'size': (SIDEBAR_IMAGE_WIDTH,SIDEBAR_IMAGE_WIDTH), 'options': []},
                        'admin_directory_listing_icon': {'size': (48,48), 'options': ['crop','upscale']},
                        'admin_tiny_icon': {'size': (32,32), 'options': ['crop','upscale']},
                    }
    file_type = 'image'
    file = thumbnail_fields.ImageWithThumbnailsField(
                    upload_to=IMAGE_FILER_UPLOAD_ROOT,
                    storage=fs,
                    #height_field='_height_field', width_field='_width_field', # the builtin django width/height sucks, because it throws an exception it the image is missing
                    thumbnail={'size': (50, 50)},
                    #extra_thumbnails={
                    #    'admin_clipboard_icon': {'size': (32,32), 'options': ['crop','upscale']},
                    #    'admin_sidebar_preview': {'size': (SIDEBAR_IMAGE_WIDTH,SIDEBAR_IMAGE_WIDTH), 'options': []},
                    #    'admin_directory_listing_icon': {'size': (48,48), 'options': ['crop','upscale']},
                    #    'admin_tiny_icon': {'size': (32,32), 'options': ['crop','upscale']},
                    #},
                    null=True, blank=True,max_length=255)
    _height_field = models.IntegerField(null=True, blank=True) 
    _width_field = models.IntegerField(null=True, blank=True)
    
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    
    contact = models.ForeignKey(auth_models.User, related_name='contact_of_files', null=True, blank=True)
    
    default_alt_text = models.CharField(max_length=255, blank=True, null=True)
    default_caption = models.CharField(max_length=255, blank=True, null=True)
    
    author = models.CharField(max_length=255, null=True, blank=True)
    
    must_always_publish_author_credit = models.BooleanField(default=False)
    must_always_publish_copyright = models.BooleanField(default=False)
    
    # TODO: Factor out customer specific fields... maybe a m2m?
    can_use_for_web = models.BooleanField(default=True)
    can_use_for_print = models.BooleanField(default=True)
    can_use_for_teaching = models.BooleanField(default=True)
    can_use_for_research = models.BooleanField(default=True)
    can_use_for_private_use = models.BooleanField(default=True)
    
    usage_restriction_notes = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    has_all_mandatory_data = models.BooleanField(default=False, editable=False)
    
    subject_location = models.CharField(max_length=64, null=True, blank=True, default=None)
    
    def _check_validity(self):
        if not self.name or not self.contact:
            return False
        return True
    def sidebar_image_ratio(self):
        if self.width:
            return float(self.width)/float(self.SIDEBAR_IMAGE_WIDTH)
        else:
            return 1.0
    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.exif.get('DateTimeOriginal',None)
                if exif_date is not None:
                    d, t = str.split(exif_date.values)
                    year, month, day = d.split(':')
                    hour, minute, second = t.split(':')
                    self.date_taken = datetime(int(year), int(month), int(day),
                                               int(hour), int(minute), int(second))
            except:
                pass
        if self.date_taken is None:
            self.date_taken = datetime.now()
        if not self.contact:
            self.contact = self.owner
        self.has_all_mandatory_data = self._check_validity()
        try:
            if self.subject_location:
                parts = self.subject_location.split(',')
                pos_x = int(parts[0])
                pos_y = int(parts[1])
                                                  
                sl = (int(pos_x), int(pos_y) )
                exif_sl = self.exif.get('SubjectLocation', None)
                if self.file and not sl == exif_sl:
                    self.file.open()
                    fd_source = StringIO.StringIO(self.file.read())
                    self.file.close()
                    set_exif_subject_location(sl, fd_source, self.file.path)
        except:
            # probably the image is missing. nevermind
            pass
        try:
            self._width_field = self.file.width
            self._height_field = self.file.height
        except:
            # probably the image is missing. nevermind.
            pass
        super(Image, self).save(*args, **kwargs)
    def _get_exif(self):
        if hasattr(self, '_exif_cache'):
            return self._exif_cache
        else:
            if self.file:
                self._exif_cache = get_exif_for_file(self.file.path)
            else:
                self._exif_cache = {}
        return self._exif_cache
    exif = property(_get_exif)
    def has_edit_permission(self, request):
        return self.has_generic_permission(request, 'edit')
    def has_read_permission(self, request):
        return self.has_generic_permission(request, 'read')
    def has_add_children_permission(self, request):
        return self.has_generic_permission(request, 'add_children')
    def has_generic_permission(self, request, type):
        """
        Return true if the current user has permission on this
        image. Return the string 'ALL' if the user has all rights.
        """
        user = request.user
        if not user.is_authenticated() or not user.is_staff:
            return False
        elif user.is_superuser:
            return True
        elif user == self.owner:
            return True
        elif self.folder:
            return self.folder.has_generic_permission(request, type)
        else:
            return False
                
    def label(self):
        if self.name in ['',None]:
            return self.original_filename or 'unnamed file'
        else:
            return self.name
    label = property(label)
    @property
    def width(self):
        return self._width_field or 0
    @property
    def height(self):
        return self._height_field or 0
    @property
    def size(self):
        try:
            return self.file.size
        except:
            return 0
    @property
    def thumbnails(self):
        # we build an extra dict here mainly
        # to prevent the default errors to 
        # get thrown and to add a default missing
        # image (not yet)
        print "getting thumbnails for %s" % self.id
        if not hasattr(self, '_thumbnails'):
            tns = {}
            #for name, tn in self.file.extra_thumbnails.items():
            #    tns[name] = tn
            #self._thumbnails = tns
            for name, opts in Image.DEFAULT_THUMBNAILS.items():
                tns[name] = unicode(self.file._build_thumbnail(opts))
            self._thumbnails = tns
            print tns
        return self._thumbnails
    @property
    def url(self):
        '''
        needed to make this behave like a ImageField
        '''
        return self.file.url
    @property
    def absolute_image_url(self):
        return self.url
    @property
    def rel_image_url(self):
        'return the image url relative to MEDIA_URL'
        try:
            rel_url = u"%s" % self.file.url
            if rel_url.startswith('/media/'):
                before, match, rel_url = rel_url.partition('/media/')
            return rel_url
        except Exception, e:
            return ''
    def __unicode__(self):
        # this simulates the way a file field works and
        # allows the sorl thumbnail tag to use the Image model
        # as if it was a image field
        return self.rel_image_url


class FolderPermissionManager(models.Manager):
    def get_read_id_list(self, user):
        """
        Give a list of a Folders where the user has read rights or the string
        "All" if the user has all rights.
        """
        return self.__get_id_list(user, "can_read")
    def get_edit_id_list(self, user):
        return self.__get_id_list(user, "can_edit")
    def get_add_children_id_list(self, user):
        return self.__get_id_list(user, "can_add_children")
    def __get_id_list(self, user, attr):
        if user.is_superuser:
            return 'All'
        allow_list = []
        deny_list = []
        group_ids = user.groups.all().values_list('id', flat=True)
        q = Q(user=user)|Q(group__in=group_ids)|Q(everybody=True)
        perms = self.filter(q).order_by('folder__tree_id', 'folder__level', 
                                        'folder__lft')
        for perm in perms:
            if perm.folder:
                folder_id = perm.folder.id
            else:
                folder_id = None
            if perm.type == FolderPermission.ALL:
                if getattr(perm, attr):
                    allow_list = list(Folder.objects.all().values_list('id', flat=True))
                else:
                    return []
            if getattr(perm, attr):
                if folder_id not in allow_list:
                    allow_list.append(folder_id)
                if folder_id in deny_list:
                    deny_list.remove(folder_id)
            else:
                if folder_id not in deny_list:
                    deny_list.append(folder_id)
                if folder_id in allow_list:
                    allow_list.remove(folder_id)
            if perm.type == FolderPermission.CHILDREN:
                for id in perm.folder.get_descendants().values_list('id', flat=True):
                    if getattr(perm, attr):
                        if id not in allow_list:
                            allow_list.append(id)
                        if id in deny_list:
                            deny_list.remove(id)
                    else:
                        if id not in deny_list:
                            deny_list.append(id)
                        if id in allow_list:
                            allow_list.remove(id)
        return allow_list
            
class FolderPermission(models.Model):
    ALL = 0
    THIS = 1
    CHILDREN = 2
    
    TYPES = (
        (ALL, _('all items') ),
        (THIS, _('this item only') ),
        (CHILDREN, _('this item and all children') ),
    )
    '''
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    '''
    folder = models.ForeignKey(Folder, null=True, blank=True)
    
    type = models.SmallIntegerField(_('type'), choices=TYPES, default=0)
    user = models.ForeignKey(auth_models.User, verbose_name=_("user"), blank=True, null=True)
    group = models.ForeignKey(auth_models.Group, verbose_name=_("group"), blank=True, null=True)
    everybody = models.BooleanField(_("everybody"), default=False)
    
    can_edit = models.BooleanField(_("can edit"), default=True)
    can_read = models.BooleanField(_("can read"), default=True)
    can_add_children = models.BooleanField(_("can add children"), default=True)
    
    objects = FolderPermissionManager()
    
    def __unicode__(self):
        if self.folder:
            name = u'%s' % self.folder
        else:
            name = u'All Folders'
        
        ug = []
        if self.everybody:
            user = 'Everybody'
        else:
            if self.group:
                ug.append(u"Group: %s" % self.group)
            if self.user:
                ug.append(u"User: %s" % self.user)
        usergroup = " ".join(ug)
        perms = []
        for s in ['can_edit', 'can_read', 'can_add_children']:
            if getattr(self, s):
                perms.append(s)
        perms = ', '.join(perms)
        return u"Folder: '%s'->%s [%s] [%s]" % (name, unicode(self.TYPES[self.type][1]), perms, usergroup)
    class Meta:
        verbose_name = _('Folder Permission')
        verbose_name_plural = _('Folder Permissions')


class Clipboard(models.Model):
    user = models.ForeignKey(auth_models.User, related_name="clipboards")
    files = models.ManyToManyField(Image, related_name="clipboards", through='ClipboardItem')
    
    def append_file(self, file):
        newitem = ClipboardItem(file=file, clipboard=self)
        newitem.save()
    
    def empty(self):
        for item in self.bucket_items.all():
            item.delete()
    empty.alters_data = True
    
    def clone(self, to_folder=None):
        pass
    def set_image_manipulation_profile(self):
        pass
    
    def __unicode__(self):
        return u"Clipboard %s of %s" % (self.id, self.user)

class ClipboardItem(models.Model):
    file = models.ForeignKey(Image)
    clipboard = models.ForeignKey(Clipboard)
    is_checked = models.BooleanField(default=True)

class DummyFolder(object):
    name = "Dummy Folder"
    is_root = True
    is_smart_folder = True
    can_have_subfolders = False
    parent = None
    _icon = "plainfolder"
    @property
    def children(self):
        return Folder.objects.filter(id__in=[0]) # empty queryset
    @property
    def files(self):
        return Image.objects.filter(id__in=[0]) # empty queryset
    parent_url = None
    @property
    def image_files(self):
        return self.files
    @property
    def icons(self):
        r = {}
        if getattr(self, '_icon', False):
            for size in DEFAULT_ICON_SIZES:
                r[size] = "%simage_filer/icons/%s_%sx%s.png" % \
                    (context_processors.media(None)['IMAGE_FILER_MEDIA_URL'],
                     self._icon, size, size)
        return r

DEFAULT_ICON_SIZES = (
        '32','48','64',
)

class UnfiledImages(DummyFolder):
    name = _("unfiled files")
    is_root = True
    _icon = "unfiled_folder"
    def _files(self):
        return Image.objects.filter(folder__isnull=True)
    files = property(_files)

class ImagesWithMissingData(DummyFolder):
    name = _("files with missing metadata")
    is_root = True
    _icon = "incomplete_metadata_folder"
    @property
    def files(self):
        return Image.objects.filter(has_all_mandatory_data=False)

class FolderRoot(DummyFolder):
    name = 'Root'
    is_root = True
    is_smart_folder = False
    can_have_subfolders = True
    @property
    def children(self):
        return Folder.objects.filter(parent__isnull=True)
    parent_url = None

if 'cms' in settings.INSTALLED_APPS:
    from cms.models import CMSPlugin, Page
    from sorl.thumbnail.main import DjangoThumbnail
    class ImagePublication(CMSPlugin):
        LEFT = "left"
        RIGHT = "right"
        FLOAT_CHOICES = ((LEFT, _("left")),
                         (RIGHT, _("right")),
                         )
        image = ImageFilerModelImageField()
        alt_text = models.CharField(null=True, blank=True, max_length=255)
        caption = models.CharField(null=True, blank=True, max_length=255)
        width = models.PositiveIntegerField(null=True, blank=True)
        height = models.PositiveIntegerField(null=True, blank=True)
        
        longdesc = models.TextField(null=True, blank=True)
        free_link = models.CharField(_("link"), max_length=255, blank=True, null=True, help_text=_("if present image will be clickable"))
        page_link = models.ForeignKey(Page, verbose_name=_("page"), null=True, blank=True, help_text=_("if present image will be clickable"))
        float = models.CharField(_("side"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES)
        
        
        
        #crop_ax = models.PositiveIntegerField(null=True, blank=True)
        #crop_ay = models.PositiveIntegerField(null=True, blank=True)
        #crop_bx = models.PositiveIntegerField(null=True, blank=True)
        #crop_by = models.PositiveIntegerField(null=True, blank=True)
        
        
        show_author = models.BooleanField(default=False)
        show_copyright = models.BooleanField(default=False)

        def save(self, *args, **kwargs):
            # default the publication's size to the image size
            if self.image and not self.width and not self.height:
                self.width = self.image.width
                self.height = self.image.height
            super(ImagePublication, self).save(*args, **kwargs)
        
        def scaled_image_url(self):
            h = self.height or 128
            w = self.width or 128
            tn = unicode(DjangoThumbnail(self.image.file, (w,h), opts=['crop','upscale'] ))
            return tn
        def __unicode__(self):
            if self.image:
                return self.image.label
            else:
                return u"Image Publication %s" % self.caption
            return ''
        @property
        def alt(self): return self.alt_text
        @property
        def url(self): return self.free_link
    
    class ImageFilerTeaser(CMSPlugin):
        """
        A Teaser
        """
        title = models.CharField(_("title"), max_length=255)
        image = ImageFilerModelImageField(blank=True, null=True)
        page_link = models.ForeignKey(Page, verbose_name=_("page"), help_text=_("If present image will be clickable"), blank=True, null=True)
        url = models.CharField(_("link"), max_length=255, blank=True, null=True, help_text=_("If present image will be clickable."))
        description = models.TextField(_("description"), blank=True, null=True)
        
        def __unicode__(self):
            return self.title
    
    class FolderPublication(CMSPlugin):
        folder = ImageFilerModelFolderField()
        class Meta:
            db_table = 'cmsplugin_imagefolder'
 
        
    if 'reversion' in settings.INSTALLED_APPS:       
        import reversion 
        reversion.register(ImagePublication, follow=["cmsplugin_ptr"])
        reversion.register(FolderPublication, follow=["cmsplugin_ptr"])
