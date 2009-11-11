from django.utils.translation import ugettext as _
from django.utils.text import truncate_words
from django.utils import simplejson
from django.db import models
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from sorl.thumbnail.base import ThumbnailException
from image_filer import context_processors

class ImageFilerImageWidget(ForeignKeyRawIdWidget):
    choices = None
    input_type = 'hidden'
    is_hidden = True
    def render(self, name, value, attrs=None):
        obj = self.obj_for_value(value)
        css_id = attrs.get('id', 'id_image_x')
        css_id_thumbnail_img = "%s_thumbnail_img" % css_id
        css_id_description_txt = "%s_description_txt" % css_id
        if attrs is None:
            attrs = {}
        related_url = reverse('admin:image_filer-directory_listing-root')
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = []
        if obj:
            try:
                output.append(u'<img id="%s" src="%s" alt="%s" /> ' % (css_id_thumbnail_img, obj.thumbnails['admin_tiny_icon'], obj.label) )
            except ThumbnailException:
                # this means that the image is missing on the filesystem
                output.append(u'<img id="%s" src="%s" alt="%s" /> ' % (css_id_thumbnail_img, '', 'image missing!') )
            output.append(u'&nbsp;<strong id="%s">%s</strong>' % (css_id_description_txt, obj) )
        else:
            output.append(u'<img id="%s" src="" class="quiet" alt="no image selected">' % css_id_thumbnail_img)
            output.append(u'&nbsp;<strong id="%s">%s</strong>' % (css_id_description_txt, '') )
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
        output.append('''<a href="" class="deletelink" onclick="return removeImageLink('%s');">&nbsp;</a>''' % (css_id,) )
        output.append('</br>')
        super_attrs = attrs.copy()
        output.append( super(ForeignKeyRawIdWidget, self).render(name, value, super_attrs) )
        return mark_safe(u''.join(output))
    def label_for_value(self, value):
        obj = self.obj_for_value(value)
        return '&nbsp;<strong>%s</strong>' % truncate_words(obj, 14)
    def obj_for_value(self, value):
        try:
            key = self.rel.get_related_field().name
            obj = self.rel.to._default_manager.get(**{key: value})
        except:
            obj = None
        return obj
    
    class Media:
        js = (context_processors.media(None)['IMAGE_FILER_MEDIA_URL']+'js/image_widget_thumbnail.js',
              context_processors.media(None)['IMAGE_FILER_MEDIA_URL']+'js/popup_handling.js',)

class ImageFilerImageFormField(forms.ModelChoiceField):
    widget = ImageFilerImageWidget 
    def __init__(self, rel, queryset, to_field_name, *args, **kwargs):
        self.rel = rel
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.max_value = None
        self.min_value = None
        other_widget = kwargs.pop('widget', None)
        forms.Field.__init__(self, widget=self.widget(rel), *args, **kwargs)

class ImageFilerModelImageField(models.ForeignKey):
    def __init__(self, **kwargs):
        from image_filer.models import Image
        return super(ImageFilerModelImageField,self).__init__(Image, **kwargs)
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        #defaults = {'form_class': ImageFilerImageWidget}
        defaults = {
            'form_class': ImageFilerImageFormField,
            'rel': self.rel,
        }
        defaults.update(kwargs)
        return super(ImageFilerModelImageField, self).formfield(**defaults)
    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.related.ForeignKey"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

class ImageFilerFolderWidget(ForeignKeyRawIdWidget):
    choices = None
    input_type = 'hidden'
    is_hidden = True
    def render(self, name, value, attrs=None):
        obj = self.obj_for_value(value)
        css_id = attrs.get('id')
        css_id_name = "%s_name" % css_id
        if attrs is None:
            attrs = {}
        related_url = reverse('admin:image_filer-directory_listing-root')
        params = self.url_parameters()
        params['select_folder'] = 1
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = []
        if obj:
            output.append(u'Folder: <span id="%s">%s</span>' % (css_id_name,obj.name))
        else:
            output.append(u'Folder: <span id="%s">none selected</span>' % css_id_name)
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
        output.append('</br>')
        super_attrs = attrs.copy()
        output.append( super(ForeignKeyRawIdWidget, self).render(name, value, super_attrs) )
        return mark_safe(u''.join(output))
    def label_for_value(self, value):
        obj = self.obj_for_value(value)
        return '&nbsp;<strong>%s</strong>' % truncate_words(obj, 14)
    def obj_for_value(self, value):
        try:
            key = self.rel.get_related_field().name
            obj = self.rel.to._default_manager.get(**{key: value})
        except:
            obj = None
        return obj
    
    class Media:
        js = (context_processors.media(None)['IMAGE_FILER_MEDIA_URL']+'js/popup_handling.js',)

class ImageFilerFolderFormField(forms.ModelChoiceField):
    widget = ImageFilerFolderWidget 
    def __init__(self, rel, queryset, to_field_name, *args, **kwargs):
        self.rel = rel
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.max_value = None
        self.min_value = None
        other_widget = kwargs.pop('widget', None)
        forms.Field.__init__(self, widget=self.widget(rel), *args, **kwargs)

class ImageFilerModelFolderField(models.ForeignKey):
    def __init__(self, **kwargs):
        from image_filer.models import Folder
        return super(ImageFilerModelFolderField,self).__init__(Folder, **kwargs)
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        #defaults = {'form_class': ImageFilerImageWidget}
        defaults = {
            'form_class': ImageFilerFolderFormField,
            'rel': self.rel,
        }
        defaults.update(kwargs)
        return super(ImageFilerModelFolderField, self).formfield(**defaults)
