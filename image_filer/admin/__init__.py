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
from django.conf import settings

#from django.contrib.admin import actions

admin.site.register([FolderPermission,])


class PrimitivePermissionAwareModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # we don't have a "add" permission... but all adding is handled
        # by special methods that go around these permissions anyway
        return False
    def has_change_permission(self, request, obj=None):
        if hasattr(obj, 'has_edit_permission'):
            if obj.has_edit_permission(request):
                #print "%s has edit permission for %s" % (request.user, obj)
                return True
            else:
                #print "%s has NO edit permission for %s" % (request.user, obj)
                return False
        else:
            return True
        
    def has_delete_permission(self, request, obj=None):
        # we don't have a specific delete permission... so we use change
        return self.has_change_permission(request, obj)

class ImageAdminFrom(forms.ModelForm):
    subject_location = forms.CharField(max_length=64, required=False)
    
    def sidebar_image_ratio(self):
        if self.instance:
            return self.instance.sidebar_image_ratio()
        else:
            return 0.0
    
    class Meta:
        model = Image

class ImageAdmin(PrimitivePermissionAwareModelAdmin):
    list_display = ('label',)
    list_per_page = 10
    search_fields = ['name', 'original_filename','default_alt_text','default_caption','usage_restriction_notes','notes', 'author']
    raw_id_fields = ('contact', 'owner',)
    
    # save_as hack, because without save_as it is impossible to hide the 
    # save_and_add_another if save_as is False.
    # To show only save_and_continue and save in the submit row we need save_as=True
    # and in render_change_form() override add and change to False.
    save_as=True
    
    form = ImageAdminFrom
    fieldsets = (
        (None, {
            'fields': ('name', 'contact', 'owner',)
        }),
        (None, {
            'fields': ('subject_location',),
            'classes': ('hide',),
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
    class Media:
        css = {
            'all': (settings.MEDIA_URL + 'image_filer/css/focal_point.css',)
        }
        js = (
            settings.MEDIA_URL + 'image_filer/js/jquery-1.3.2.min.js',
            settings.MEDIA_URL + 'image_filer/js/raphael.js',
            settings.MEDIA_URL + 'image_filer/js/focal_point.js',
        )
    def admin_thumbnail(self,xs):
        return mark_safe('<img src="{{ IMAGE_FILER_MEDIA_URL }}icons/plainfolder_32x32.png" alt="Folder Icon" />')
    admin_thumbnail.allow_tags = True
    def response_change(self, request, obj):
        '''
        Overrides the default to be able to forward to the directory listing
        instead of the default change_list_view
        '''
        r = super(ImageAdmin, self).response_change(request, obj)
        #print r['Location']
        if r['Location']:
            # it was a successful save
            if r['Location'] in ['../']:
                # this means it was a save: redirect to the directory view
                if obj.folder:
                    url = reverse('admin:image_filer-directory_listing', 
                                  kwargs={'folder_id': obj.folder.id})
                else:
                    url = reverse('admin:image_filer-directory_listing-unfiled_images')
                return HttpResponseRedirect(url)
            else:
                # this means it probably was a save_and_continue_editing
                pass
        return r
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        extra_context = {'show_delete': True}
        context.update(extra_context)
        return super(ImageAdmin, self).render_change_form(request=request, context=context, add=False, change=False, form_url=form_url, obj=obj)
    
    def delete_view(self, request, object_id, extra_context=None):
        '''
        Overrides the default to enable redirecting to the directory view after
        deletion of a image.
        
        we need to fetch the object and find out who the parent is
        before super, because super will delete the object and make it impossible
        to find out the parent folder to redirect to.
        '''
        parent_folder = None
        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
            parent_folder = obj.folder
        except self.model.DoesNotExist:
            obj = None
        
        r = super(ImageAdmin, self).delete_view(request=request, object_id=object_id, extra_context=extra_context)
        
        url = r.get("Location", None)
        if url in ["../../../../","../../"]:
            if parent_folder:
                url = reverse('admin:image_filer-directory_listing', 
                                  kwargs={'folder_id': parent_folder.id})
            else:
                url = reverse('admin:image_filer-directory_listing-unfiled_images')
            return HttpResponseRedirect(url)
        return r
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(ImageAdmin, self).get_urls()
        from image_filer import views
        url_patterns = patterns('',
            url(r'^(?P<image_id>\d+)/export/$', self.admin_site.admin_view(views.export_image), name='image_filer-export_image'),
        )
        url_patterns.extend(urls)
        return url_patterns
    def add_view(self, request):
        return HttpResponseRedirect(reverse('admin:image_filer-directory_listing-root'))
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(reverse('admin:image_filer-directory_listing-root'))

admin.site.register(Image, ImageAdmin)

class AddFolderPopupForm(forms.ModelForm):
    folder = forms.HiddenInput()
    class Meta:
        model=Folder
        fields = ('name',)
        

class FolderAdmin(PrimitivePermissionAwareModelAdmin):
    list_display = ('name',)
    exclude = ('parent',)
    list_per_page = 20
    list_filter = ('owner',)
    search_fields = ['name', 'image_files__name' ]
    raw_id_fields = ('owner',)
    save_as=True # see ImageAdmin
    #hide_in_app_index = True # custom var handled in app_index.html of image_filer
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        parent_id = request.REQUEST.get('parent_id', None)
        if parent_id:
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
        '''
        Overrides the default to be able to forward to the directory listing
        instead of the default change_list_view
        '''
        r = super(FolderAdmin, self).response_change(request, obj)
        if r['Location']:
            print r['Location']
            print obj
            # it was a successful save
            if r['Location'] in ['../']:
                if obj.parent:
                    url = reverse('admin:image_filer-directory_listing', 
                                  kwargs={'folder_id': obj.parent.id})
                else:
                    url = reverse('admin:image_filer-directory_listing-root')
                return HttpResponseRedirect(url)
            else:
                # this means it probably was a save_and_continue_editing
                pass
        return r
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        extra_context = {'show_delete': True}
        context.update(extra_context)
        return super(FolderAdmin, self).render_change_form(request=request, context=context, add=False, change=False, form_url=form_url, obj=obj)
    
    def delete_view(self, request, object_id, extra_context=None):
        '''
        Overrides the default to enable redirecting to the directory view after
        deletion of a folder.
        
        we need to fetch the object and find out who the parent is
        before super, because super will delete the object and make it impossible
        to find out the parent folder to redirect to.
        '''
        parent_folder = None
        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
            parent_folder = obj.parent
        except self.model.DoesNotExist:
            obj = None
        
        r = super(FolderAdmin, self).delete_view(request=request, object_id=object_id, extra_context=extra_context)
        url = r.get("Location", None)
        if url in ["../../../../","../../"]:
            if parent_folder:
                url = reverse('admin:image_filer-directory_listing', 
                                  kwargs={'folder_id': parent_folder.id})
            else:
                url = reverse('admin:image_filer-directory_listing-root')
            return HttpResponseRedirect(url)
        return r
    def icon_img(self,xs):
        return mark_safe('<img src="{{ IMAGE_FILER_MEDIA_URL }}img/icons/plainfolder_32x32.png" alt="Folder Icon" />')
    icon_img.allow_tags = True
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(FolderAdmin, self).get_urls()
        from image_filer import views
        url_patterns = patterns('',
            # we override the default list view with our own directory listing of the root directories
            url(r'^$', self.admin_site.admin_view(views.directory_listing), name='image_filer-directory_listing-root'),
            url(r'^(?P<folder_id>\d+)/list/$', self.admin_site.admin_view(views.directory_listing), name='image_filer-directory_listing'),
            
            url(r'^(?P<folder_id>\d+)/make_folder/$', self.admin_site.admin_view(views.make_folder), name='image_filer-directory_listing-make_folder'),
            url(r'^make_folder/$', self.admin_site.admin_view(views.make_folder), name='image_filer-directory_listing-make_root_folder'),
            
            url(r'^images_with_missing_data/$', self.admin_site.admin_view(views.directory_listing), {'viewtype': 'images_with_missing_data'}, name='image_filer-directory_listing-images_with_missing_data'),
            url(r'^unfiled_images/$', self.admin_site.admin_view(views.directory_listing), {'viewtype': 'unfiled_images'}, name='image_filer-directory_listing-unfiled_images'),
        )
        url_patterns.extend(urls)
        return url_patterns   
    
admin.site.register(Folder, FolderAdmin)

class ClipboardItemInline(admin.TabularInline):
    model = ClipboardItem
class ClipboardAdmin(admin.ModelAdmin):
    model = Clipboard
    inlines = [ ClipboardItemInline, ]
    filter_horizontal = ('files',)
    raw_id_fields = ('user',)
    verbose_name = "DEBUG Clipboard"
    verbose_name_plural = "DEBUG Clipboards"
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(ClipboardAdmin, self).get_urls()
        from image_filer import views
        url_patterns = patterns('',
            #url(r'^([0-9]+)/move-page/$', self.admin_site.admin_view(self.move_entity), name='%s_%s' % (info, 'move_page') ),
            url(r'^operations/paste_clipboard_to_folder/$', self.admin_site.admin_view(views.paste_clipboard_to_folder), name='image_filer-paste_clipboard_to_folder'),
            url(r'^operations/discard_clipboard/$', self.admin_site.admin_view(views.discard_clipboard), name='image_filer-discard_clipboard'),
            url(r'^operations/delete_clipboard/$', self.admin_site.admin_view(views.delete_clipboard), name='image_filer-delete_clipboard'),
            url(r'^operations/move_file_to_clipboard/$', self.admin_site.admin_view(views.move_file_to_clipboard), name='image_filer-move_file_to_clipboard'),
            # upload does it's own permission stuff (because of the stupid flash missing cookie stuff)
            url(r'^operations/upload/$', views.ajax_upload, name='image_filer-ajax_upload'),
        )
        url_patterns.extend(urls)
        return url_patterns
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Clipboard, ClipboardAdmin)