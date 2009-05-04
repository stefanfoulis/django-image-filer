from django.utils.translation import ugettext as _
from django.utils.text import truncate_words
from django.db import models
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings

class ImageFilerImageWidget(ForeignKeyRawIdWidget):
    choices = None
    def render(self, name, value, attrs=None):
        obj = self.obj_for_value(value)
        if attrs is None:
            attrs = {}
        related_url = reverse('image_filer-directory_listing-root')
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = []
        if obj:
            output.append(u'<img src="%s" alt="%s" /> ' % (obj.get_admin_thumbnail_url(), obj.label) )
        
        output.append( super(ForeignKeyRawIdWidget, self).render(name, value, attrs) )
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
        if value:
            output.append(self.label_for_value(value))
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

class ImageFilerImageFormField(forms.ModelChoiceField):
    widget = ImageFilerImageWidget 
    def __init__(self, rel, queryset, to_field_name, *args, **kwargs):
        self.rel = rel
        self.queryset = queryset
        self.to_field_name = to_field_name
        self.max_value = None
        self.min_value = None
        forms.Field.__init__(self, widget=self.widget(rel), *args, **kwargs)

class ImageFilerModelImageField(models.ForeignKey):
    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        #defaults = {'form_class': ImageFilerImageWidget}
        defaults = {
            'form_class': ImageFilerImageFormField,
            'rel': self.rel,
        }
        defaults.update(kwargs)
        print defaults
        return super(ImageFilerModelImageField, self).formfield(**defaults)