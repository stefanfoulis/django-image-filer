from django.contrib import admin
from image_filer.models import  *
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.contrib.admin.util import unquote, flatten_fieldsets, get_deleted_objects, model_ngettext, model_format_dict
from django import forms
from django.utils.translation import ugettext as _
from django.utils.translation import ngettext, ugettext_lazy
from django.utils.encoding import force_unicode

from django.contrib.admin import actions

admin.site.register([FolderPermission, ImagePermission])

class Directory(Folder):
    """
    Dummy Directory Model to allow the addition of an entry in the app menu
    """
    class Meta:
        proxy = True
        verbose_name = "Directory Listing"
        verbose_name_plural = "Directory Listing"

class DirectoryAdmin(admin.ModelAdmin):
    pass
admin.site.register([Directory], DirectoryAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ('label','admin_thumbnail', 'has_all_mandatory_data')
    list_per_page = 10
    search_fields = ['name', 'original_filename','default_alt_text','default_caption','usage_restriction_notes','notes', 'author']
    raw_id_fields = ('contact', 'owner',)
    fieldsets = (
        (None, {
            'fields': ('name', 'contact', 'owner', )
        }),
        ('Copyright and Author', {
            #'classes': ('collapse',),
            'fields': ('author', 'must_always_publish_author_credit', 'must_always_publish_copyright')
        }),
        ('Restrictions', {
            #'classes': ('collapse',),
            'fields': ('can_use_for_web', 'can_use_for_print','can_use_for_teaching','can_use_for_research','can_use_for_private_use')
        }),
        #('Manipulation (only works with cloned images)', {
            #'classes': ('collapse',),
        #    'fields': ('manipulation_profile', )
        #}),
    )
    def response_change(self, request, obj):
        r = super(ImageAdmin, self).response_change(request, obj)
        if r['Location']:
            if obj.folder:
                url = reverse('image_filer-directory_listing', 
                              kwargs={'folder_id': obj.folder.id})
            else:
                url = reverse('image_filer-directory_listing-unfiled_images')
            return HttpResponseRedirect(url)
        return r
admin.site.register(Image, ImageAdmin)
#X = ["image_files__%s" % x for x in ImageAdmin.search_fields]

class AddFolderPopupForm(forms.ModelForm):
    folder = forms.HiddenInput()
    class Meta:
        model=Folder
        fields = ('name',)
        

class FolderAdmin(admin.ModelAdmin):
    list_display = ('icon_img', 'name',)
    exclude = ('parent',)
    #list_display_links = ('icon_img', 'name', )
    list_editable =('name', )
    list_per_page = 20
    list_filter = ('owner',)
    verbose_name = "DEBUG Folder Admin"
    search_fields = ['name', 'image_files__name' ]
    hide_in_appindex = True
    raw_id_fields = ('owner',)
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        parent_id = request.REQUEST.get('parent_id', None)
        if parent_id:
            print "yay! has a parent1"
            return AddFolderPopupForm
        else:
            return super(FolderAdmin, self).get_form(request, obj=None, **kwargs)
    def save_form(self, request, form, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        r = form.save(commit=False)
        parent_id = request.REQUEST.get('parent_id', None)
        if parent_id:
            parent = Folder.objects.get(id=parent_id)
            r.parent = parent
        return r
    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        r = super(FolderAdmin, self).response_change(request, obj)
        if r['Location']:
            # this must have been a successful save... do the hackish trickery
            if obj.parent:
                url = reverse('image_filer-directory_listing', 
                              kwargs={'folder_id': obj.parent.id})
            else:
                url = reverse('image_filer-directory_listing-root')
            return HttpResponseRedirect(url)
        return r
    
    def icon_img(self,xs):
        return mark_safe('<img src="/media/img/icons/plainfolder_32x32.png" alt="Folder Icon" />')
    icon_img.allow_tags = True
admin.site.register(Folder, FolderAdmin)

class ImageManipulationStepInline(admin.TabularInline):
    model = ImageManipulationStep
    fieldsets = (
        (None, {
            'fields': ('filter_identifier', 'data', 'order')
        }),
    )
class ImageManipulationProfileAdmin(admin.ModelAdmin):
    inlines = [ ImageManipulationStepInline, ]
admin.site.register(ImageManipulationProfile, ImageManipulationProfileAdmin)
admin.site.register([ImageManipulationTemplate])



class ClipboardItemInline(admin.TabularInline):
    model = ClipboardItem
class ClipboardAdmin(admin.ModelAdmin):
    model = Clipboard
    inlines = [ ClipboardItemInline, ]
    filter_horizontal = ('files',)
    raw_id_fields = ('user',)
    verbose_name = "DEBUG Clipboard"
#admin.site.register(Clipboard, ClipboardAdmin)