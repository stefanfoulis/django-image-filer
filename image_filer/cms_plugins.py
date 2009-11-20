from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from image_filer.models import ImagePublication, ImageFilerTeaser, FolderPublication

class ImagePlugin(CMSPluginBase):
    model = ImagePublication
    name = _("Image (image filer)")
    render_template = "cms/plugins/image.html"
    text_enabled = True
    raw_id_fields = ('image',)
    
    def render(self, context, instance, placeholder):
        if not instance.width:
            try:
                theme = context['theme']
                width = int(theme.split('_')[0]) * 60
                if width < 960:
                    width -= 20
            except (KeyError, IndexError):
                width = ''
        else:
            width = instance.width
        if instance.height:
            height = instance.height
        else:
            height = '1000'
        if instance.free_link:
            link = instance.free_link
        elif instance.page_link:
            link = instance.page_link.get_absolute_url()
        else:
            link = ""
        context.update({
            'picture':instance,
            'link':link, 
            'image_size': u'%sx%s' % (width, height),
            'placeholder':placeholder
        })
        return context
    def icon_src(self, instance):
        return instance.image.thumbnails['admin_tiny_icon']
plugin_pool.register_plugin(ImagePlugin)

class ImageFilerTeaserPlugin(CMSPluginBase):
    model = ImageFilerTeaser
    name = _("Teaser (image filer)")
    render_template = "cms/plugins/teaser.html"
    
    def render(self, context, instance, placeholder):
        if instance.url:
            link = instance.url
        elif instance.page_link:
            link = instance.page_link.get_absolute_url()
        else:
            link = ""
        context.update({
            'object':instance, 
            'placeholder':placeholder,
            'link':link
        })
        return context
plugin_pool.register_plugin(ImageFilerTeaserPlugin)

class ImageFolderPlugin(CMSPluginBase):
    model = FolderPublication
    name = _("Image Folder from Filer")
    render_template = "image_filer/folder.html"
    text_enabled = True
    #change_form_template = 'admin/image_filer/cms/image_plugin/change_form.html'
    raw_id_fields = ('folder',)
    
    def render(self, context, instance, placeholder):
        context.dicts.append({'image_folder_publication':instance, 'placeholder':placeholder})
        return context
    def icon_src(self, instance):
        return "(none)"
plugin_pool.register_plugin(ImageFolderPlugin)

class FolderSlideshowPlugin(ImageFolderPlugin):
    name = _("Slideshow of image folder")
    class Meta:
        proxy = True
    render_template = "image_filer/slideshow2.html"
plugin_pool.register_plugin(FolderSlideshowPlugin)
