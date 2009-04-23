import os
import mptt
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, date
from utils import EXIF
from fields import PickledObjectField
from django.db.models.signals import post_init
from django.utils.functional import curry

from django.contrib.auth import models as auth_models

from django.conf import settings

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
print settings.MEDIA_URL
uuid_file_system_storage = UUIDFileSystemStorage( 
                                location=CATALOGUE_BASE_PATH,
                                base_url=CATALOGUE_BASE_URL
                                )

class AbstractFile(models.Model):
    """
    Represents a "File-ish" thing that is in a Folder. Any subclasses must
    at least define a foreign key to folder and a file field (or subclass thereof):
        folder = models.ForeignKey(Folder, related_name='mytype_files')
        file = models.FileField(upload_to='catalogue', storage=uuid_file_system_storage)
    Additional attributes may be added to enhance the experience:
        get_absolute_url(): link to the object in the front-end
        get_absolute_admin_url(): link to the object in the admin interface
        get_default_thumbnail_url(): the thumbnail to show in default listings
        get_admin_thumbnail_url(): the thumbnail for admin listings
        file_type: 
    """
    file_type = 'unknown'
    original_filename = models.CharField(editable=False, max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    owner = models.ForeignKey(auth_models.User, related_name='owned_files', null=True, blank=True)
    
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


class FolderRoot(object):
    name = 'Root'
    
    def _children(self):
        return Folder.objects.filter(parent__isnull=True)
    children = property(_children)

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
    
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    
    owner = models.ForeignKey(auth_models.User, related_name='owned_folders', null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    @property
    def files(self):
        # TODO: make this a "multi iterator" that can iterate over multiple
        #         querysets without having to load all objects
        rel = []
        for attr in dir(self):
            if not attr.startswith('_') and attr.endswith('_files'):
                # TODO: also check for fieldtype
                rel.append(attr)
        result = []
        for r in rel:
            files = getattr(self,r)
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
        return u"<%s: '%s'>" % (self.__class__.__name__, self.name)
    class Meta:
        unique_together = (('parent','name'),)

class Image(AbstractFile):
    file_type = 'image'
    file = models.ImageField(upload_to='catalogue', storage=uuid_file_system_storage, height_field='_file_height', width_field='_file_witdh', null=True, blank=True)
    _height_field = models.IntegerField(null=True, blank=True) 
    _width_field = models.IntegerField(null=True, blank=True)
    
    date_taken = models.DateTimeField(_('date taken'), null=True, blank=True, editable=False)
    
    manipulation_profile = models.ForeignKey('ImageManipulationProfile', related_name="images", null=True, blank=True)
    
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    folder = models.ForeignKey(Folder, related_name='image_files', null=True, blank=True)
    
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
    
    def render(self):
        if not self.parent:
            # if this is a root image rendering is forbidden... the original
            # may not be changed
            return False
        if not self.file and self.parent:
            # this is a child image that has no file set yet... generate an id
            file_ext = os.path.splitext(self.parent.file.name)[1]
            new_uuid = uuid.uuid4()
            self.file = "gen-%s.%s" % (new_uuid, file_ext)
        im = filters.Image.open(self.parent.file.path)
        # Save the original format
        im_format = im.format
        if self.manipulation_profile:
            im = self.manipulation_profile.render(im)
        im_filename = '%s' % (self.file.path)
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return im
                except KeyError:
                    pass
            im.save(im_filename, 'JPEG')
        except IOError, e:
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e

    def admin_thumbnail(self):
        func = getattr(self, 'get_admin_thumbnail_url', None)
        if func is None:
            return _('An "admin_thumbnail" photo size has not been defined.')
        else:
            if hasattr(self, 'get_absolute_url'):
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.get_absolute_url(), func())
            else:
                return u'<a href="%s"><img src="%s"></a>' % \
                    (self.image.url, func())
    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True
    
    def cache_path(self):
        if self.file:
            return os.path.join(os.path.dirname(self.file.path),"cache")
    cache_path = property(cache_path)
    def cache_url(self):
        if self.file:
            return '/'.join([os.path.dirname(self.file.url), "cache"])
    cache_url = property(cache_url)
    
    def _image_filename(self):
        if self.file:
            return os.path.basename(self.file.path)
    image_filename = property(_image_filename)
    
    def _get_filename_for_template(self, template):
        """
        template: either a ImageManipulationTemplate instance or just a simple
        string representing the identifier of one.
        """
        template = getattr(template, 'identifier', template)
        base, ext = os.path.splitext(self.image_filename)
        return ''.join([base, '_', template, ext])
    
    def _get_TEMPLATE_template(self, template):
        return ImageManipulationTemplateCache().templates.get(template)
    
    def _get_TEMPLATE_size(self, template):
        template = ImageManipulationTemplateCache().templates.get(template)
        if not self.template_file_exists(template):
            self.create_template_file(template)
        return filters.Image.open(self._get_TEMPLATE_filename(template)).size
    
    def _get_TEMPLATE_url(self, template):
        template = ImageManipulationTemplateCache().templates.get(template)
        if not self.cached_template_file_exists(template):
            print "generating cache image"
            self.create_template_file_cache(template)
        return '/'.join( [self.cache_url, self._get_filename_for_template(template)] )
    
    def _get_TEMPLATE_filename(self, template):
        template = ImageManipulationTemplateCache().templates.get(template)
        return os.path.join( self.cache_path, self._get_filename_for_template(template) )
    
    def add_accessor_methods(self, *args, **kwargs):
        for template in ImageManipulationTemplateCache().templates.keys():
            setattr(self, 'get_%s_template' % template,
                    curry(self._get_TEMPLATE_template, template=template))
            setattr(self, 'get_%s_size' % template,
                    curry(self._get_TEMPLATE_size, template=template))
            setattr(self, 'get_%s_url' % template,
                    curry(self._get_TEMPLATE_url, template=template))
            setattr(self, 'get_%s_filename' % template,
                    curry(self._get_TEMPLATE_filename, template=template))
    
    def cached_template_file_exists(self, template):
        """
        checks if the image for this template exists
        """
        func = getattr(self, "get_%s_filename" % template.identifier, None)
        if func is not None:
            if os.path.isfile(func()):
                return True
        return False
    
    def create_template_file_cache(self, template):
        """
        creates the image for this template in the cache 
        """
        if self.cached_template_file_exists(template):
            return
        if not os.path.isdir(self.cache_path):
            os.makedirs(self.cache_path)
        try:
            im = filters.Image.open(self.file.path)
        except IOError:
            return
        # Save the original format
        im_format = im.format
        #print im_format
        # Apply the filters
        im = template.render(im)
        im_filename = getattr(self, "get_%s_filename" % template.identifier)()
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return
                except KeyError:
                    pass
            im.save(im_filename, 'JPEG')
        except IOError, e:
            print "error: ", e
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e
    def remove_cache_template_file(self, template, remove_dirs=True):
        if not self.cached_template_file_exists(template):
            return
        filename = getattr(self, "get_%s_filename" % template.identifier)()
        if os.path.isfile(filename):
            os.remove(filename)
        if remove_dirs:
            self.remove_cache_dirs()
    def clear_cache(self):
        cache = ImageManipulationTemplateCache()
        for template in cache.templates.values():
            self.remove_cache_template_file(template, remove_dirs=False)
        self.remove_cache_dirs()
    
    def pre_cache(self):
        cache = ImageManipulationTemplateCache()
        for template in cache.templates.values():
            if template.pre_cache:
                self.create_template_file_cache(template)
    def remove_cache_dirs(self):
        try:
            os.removedirs(self.cache_path)
        except:
            pass
    def get_absolute_url(self):
        # TODO: fix url do be more robust
        return '%s%s' % (CATALOGUE_BASE_URL,self.file.name)
    
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
        self.render()
        if self._get_pk_val():
            self.clear_cache()
        if not self.contact:
            self.contact = self.owner
        self.has_all_mandatory_data = self._check_validity()
        super(Image, self).save(*args, **kwargs)
        self.pre_cache()
    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(Image, self).delete()
        #check that all mandatory data is set and save the result to has_all_mandatory_data
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
mptt_models = [Folder, Image]
for mptt_model in mptt_models:
    try:
        mptt.register(mptt_model)
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
        


import filters
FILTER_CHOICES = []
for filter in filters.filters:
    FILTER_CHOICES.append( (filter.identifier, filter.name) )
#print filters.filters
#print FILTER_CHOICES

class ImageManipulationProfile(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    show_in_library = models.BooleanField(default=False)
    
    def render_to_file(self, image):
        #prepare directories
        cache_path = image.cache_path
        if not os.path.isdir(cache_path):
            os.makedirs(cache_path)
        im = filters.Image.open(image.file.path)
        # Save the original format
        im_format = im.format
        im = self.render(im)
        im_filename = '%s%s' % (cache_path, image.file.name)
        #print image.file.path
        #print cache_path
        #print im_filename
        try:
            if im_format != 'JPEG':
                try:
                    im.save(im_filename)
                    return im
                except KeyError:
                    pass
            im.save(im_filename, 'JPEG')
        except IOError, e:
            if os.path.isfile(im_filename):
                os.unlink(im_filename)
            raise e
    def render(self, im):
        for step in self.steps.order_by('order'):
            im = step.render(im)
        return im
    def __unicode__(self):
        return self.name
        

class ImageManipulationStep(models.Model):
    template = models.ForeignKey(ImageManipulationProfile, related_name='steps')
    filter_identifier = models.CharField(max_length=255, choices=FILTER_CHOICES)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    data = PickledObjectField(default={})
    order = models.IntegerField(default=0)
    
    def render(self, im):
        FilterClass = filters.filters_by_identifier[self.filter_identifier]
        filter_class_instance = FilterClass()
        return filter_class_instance.render(im)
    
    class Meta:
        ordering = ("order",)
        unique_together = (("template","order"),)

class ImageManipulationTemplate(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    profile = models.ForeignKey(ImageManipulationProfile, related_name='templates')
    
    pre_cache = models.BooleanField(_('pre-cache?'), default=False, help_text=_('If selected this photo size will be pre-cached as photos are added.'))
    
    def render(self, im):
        return self.profile.render(im)
    
    def clear_cache(self):
        for cls in Image.__subclasses__():
            for obj in cls.objects.all():
                obj.remove_cache_template_file(self)
                if self.pre_cache:
                    obj.create_template_file_cache(self)
        ImageManipulationTemplateCache().reset()
    def save(self, *args, **kwargs):
        super(ImageManipulationTemplate, self).save(*args, **kwargs)
        ImageManipulationTemplateCache().reset()
        self.clear_cache()

    def delete(self):
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)
        self.clear_cache()
        super(ImageManipulationTemplate, self).delete()
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.identifier)
class ImageManipulationTemplateCache(object):
    __state = {"templates": {}}    
    def __init__(self):
        self.__dict__ = self.__state
        if not len(self.templates):
            templates = ImageManipulationTemplate.objects.all()
            for template in templates:
                self.templates[template.identifier] = template

    def reset(self):
        self.templates = {}
# Set up the accessor methods
def add_methods(sender, instance, signal, *args, **kwargs):
    """ Adds methods to access sized images (urls, paths)

    after the Photo model's __init__ function completes,
    this method calls "add_accessor_methods" on each instance.
    """
    if hasattr(instance, 'add_accessor_methods'):
        instance.add_accessor_methods()

# connect the add_accessor_methods function to the post_init signal
post_init.connect(add_methods)


class Bucket(models.Model):
    user = models.ForeignKey(auth_models.User, related_name="buckets")
    files = models.ManyToManyField(Image, related_name="buckets", through='BucketItem')
    
    def append_file(self, file):
        newitem = BucketItem(file=file, bucket=self)
        newitem.save()
    
    def empty(self):
        for item in self.bucket_items.all():
            item.delete()
    empty.alters_data = True
    
    def create_zip(self):
        return 'zipfile'
    def clone(self, to_folder=None):
        pass
    def set_image_manipulation_profile(self):
        pass
    
    def __unicode__(self):
        return u"Bucket %s of %s" % (self.id, self.user)

class BucketItem(models.Model):
    file = models.ForeignKey(Image)
    bucket = models.ForeignKey(Bucket)
    is_checked = models.BooleanField(default=True)
    