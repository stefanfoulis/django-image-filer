from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext_lazy as _
from image_filer.models import ImagePublication
from cms.settings import CMS_MEDIA_URL
#from image_filer.forms import ImagePublicationForm

class ImagePlugin(CMSPluginBase):
    model = ImagePublication
    name = _("Image from Image Filer")
    render_template = "image_filer/cms/image.html"
    text_enabled = True
    #form = ImagePublicationForm
    #raw_id_fields = ('image',)
    
    def render(self, context, instance, placeholder):
        return {'image':instance, 'placeholder':placeholder}
    
    def icon_src(self, instance):
        # TODO - possibly use 'instance' and provide a thumbnail image
        return CMS_MEDIA_URL + u"images/plugins/image.png"
 
plugin_pool.register_plugin(ImagePlugin)