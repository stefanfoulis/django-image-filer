import os
import mptt
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date
from image_filer.utils import EXIF
from sorl.thumbnail.fields import ImageWithThumbnailsField
from image_filer.fields import ImageFilerModelImageField
# hack, so admin filters get loaded
#from image_filer.admin import filters as admin_filters

from managers import FolderManager
from django.db.models.signals import post_init
from django.utils.functional import curry
from django.core.urlresolvers import reverse

from django.contrib.auth import models as auth_models

from django.conf import settings


'''
# remove the uuid stuff for now
try:
    import uuid
except ImportError:
    from django_extensions.utils import uuid

class UUIDFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name):
        newuuid = uuid.uuid4()
        file_extension = name.split('.')[-1].lower()
        r = '%s.%s' % (newuuid, file_extension)
        return r
CATALOGUE_BASE_URL = "".join([settings.MEDIA_URL, 'catalogue/'])
CATALOGUE_BASE_PATH = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'catalogue/'))
uuid_file_system_storage = UUIDFileSystemStorage( 
                                location=CATALOGUE_BASE_PATH,
                                base_url=CATALOGUE_BASE_URL
                                )
'''
class AbstractFile(models.Model):
    """
    Represents a "File-ish" thing that is in a Folder. Any subclasses must
    at least define a foreign key to folder and a file field (or subclass thereof):
        path: return the full absolute path to the physical file (may be omited in special cases)
        file: return a file object
    Additional attributes may be added to enhance the experience:
        get_absolute_url(): link to the object in the front-end
        get_absolute_admin_url(): link to the object in the admin interface
        get_default_thumbnail_url(): the thumbnail to show in default listings
        get_admin_thumbnail_url(): the thumbnail for admin listings
        file_type: 
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
                #print attr
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

class Image(AbstractFile):
    file_type = 'image'
    file = ImageWithThumbnailsField(
                    upload_to='catalogue',
                    #storage=uuid_file_system_storage,
                    height_field='_height_field', width_field='_width_field', 
                    thumbnail={'size': (50, 50)},
                    extra_thumbnails={
                        'admin_clipboard_icon': {'size': (32,32), 'options': ['crop','upscale']},
                        'admin_sidebar_preview': {'size': (210,210), 'options': ['crop',]},
                        'admin_directory_listing_icon': {'size': (48,48), 'options': ['crop','upscale']},
                    },
                    null=True, blank=True)
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
    
    def _check_validity(self):
        if not self.name or not self.contact:
            return False
        return True
    
    def save(self, *args, **kwargs):
        if self.date_taken is None:
            try:
                exif_date = self.EXIF.get('EXIF DateTimeOriginal',None)
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
        super(Image, self).save(*args, **kwargs)
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
        else:
            att_name = "permission_%s_cache" % type
            if not hasattr(self, "permission_user_cache") or \
               not hasattr(self, att_name) or \
               request.user.pk != self.permission_user_cache.pk:
                func = getattr(ImagePermission.objects, "get_%s_id_list" % type)
                permission = func(user)
                self.permission_user_cache = request.user
                if permission == "All" or self.id in permission:
                    setattr(self, att_name, True)
                    self.permission_edit_cache = True
                else:
                    setattr(self, att_name, False)
            return getattr(self, att_name)
    def label(self):
        if self.name in ['',None]:
            return self.original_filename or 'unnamed file'
        else:
            return self.name
    label = property(label)
    def __unicode__(self):
        return self.label

# MPTT registration
try:
    mptt.register(Folder)
except mptt.AlreadyRegistered:
    pass


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
            if perm.type == FolderPermission.ALL:
                if getattr(perm, attr):
                    allow_list = list(Folder.objects.all().values_list('id', flat=True))
                else:
                    return []
            if getattr(perm, attr):
                if perm.folder.id not in allow_list:
                    allow_list.append(perm.folder.id)
                if perm.folder.id in deny_list:
                    deny_list.remove(perm.folder.id)
            else:
                if perm.folder.id not in deny_list:
                    deny_list.append(perm.folder.id)
                if perm.folder.id in allow_list:
                    allow_list.remove(perm.folder.id)
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
    can_read = models.BooleanField(_("can read"), default=False)
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
        
        return u"%s (%s)" % (usergroup, unicode(self.TYPES[self.type][1]))
    class Meta:
        verbose_name = _('Folder Permission')
        verbose_name_plural = _('Folder Permissions')
    
    

class ImagePermissionManager(models.Manager):
    def get_read_id_list(self, user):
        """
        Give a list of a Images where the user has read rights or the string
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
        perms = self.filter(q).order_by('image__tree_id', 'image__level', 
                                        'image__lft')
        for perm in perms:
            if perm.type == ImagePermission.ALL:
                if getattr(perm, attr):
                    allow_list = list(Image.objects.all().values_list('id', flat=True))
                else:
                    return []
            if getattr(perm, attr):
                if perm.image.id not in allow_list:
                    allow_list.append(perm.image.id)
                if perm.image.id in deny_list:
                    deny_list.remove(perm.image.id)
            else:
                if perm.image.id not in deny_list:
                    deny_list.append(perm.image.id)
                if perm.image.id in allow_list:
                    allow_list.remove(perm.image.id)
            if perm.type == ImagePermission.CHILDREN:
                for id in perm.image.get_descendants().values_list('id', flat=True):
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

class ImagePermission(models.Model):
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
    image = models.ForeignKey(Image, null=True, blank=True)
    
    type = models.SmallIntegerField(_('type'), choices=TYPES, default=0)
    user = models.ForeignKey(auth_models.User, verbose_name=_("user"), blank=True, null=True)
    group = models.ForeignKey(auth_models.Group, verbose_name=_("group"), blank=True, null=True)
    everybody = models.BooleanField(_("everybody"), default=False)
    
    can_edit = models.BooleanField(_("can edit"), default=True)
    can_read = models.BooleanField(_("can read"), default=False)
    can_add_children = models.BooleanField(_("can add children"), default=True)
    
    objects = ImagePermissionManager()
    
    def __unicode__(self):
        return u"%s: %s" % (self.user or self.group, unicode(self.TYPES[self.type][1]))
    class Meta:
        verbose_name = _('Image Permission')
        verbose_name_plural = _('Image Permissions')


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
    can_have_subfolders = False
    parent = None
    children = Folder.objects.filter(id__in=[0]) # empty queryset
    files = Image.objects.filter(id__in=[0]) # empty queryset
    parent_url = None
    @property
    def image_files(self):
        return self.files

class UnfiledImages(DummyFolder):
    name = "Unfiled Files"
    is_root = True
    def _files(self):
        return Image.objects.filter(folder__isnull=True)
    files = property(_files)

class ImagesWithMissingData(DummyFolder):
    name = "Unfiled Files"
    is_root = True
    def _files(self):
        return Image.objects.filter(has_all_mandatory_data=False)
    files = property(_files)
    
class FolderRoot(DummyFolder):
    name = 'Root'
    is_root = True
    can_have_subfolders = True
    
    def _children(self):
        return Folder.objects.filter(parent__isnull=True)
    children = property(_children)
    parent_url = None


if 'cms' in settings.INSTALLED_APPS:
    from cms.models import CMSPlugin
    class ImagePublication(CMSPlugin):
        image = ImageFilerModelImageField(Image)
        alt_text = models.CharField(null=True, blank=True, max_length=255)
        caption = models.CharField(null=True, blank=True, max_length=255)
        show_author = models.BooleanField(default=False)
        show_copyright = models.BooleanField(default=False)
        
        def __unicode__(self):
            if self.image:
                return self.image.label
            else:
                return u"Image Publication %s" % self.caption
            return ''
        