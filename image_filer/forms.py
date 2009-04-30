from django.forms.models import ModelForm
from image_filer.models import ImagePublication
from django import forms
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

# Not Used
class ImagePublicationForm(ModelForm):
    image = ForeignKeyRawIdWidget('Image')
    class Meta:
        model = ImagePublication
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')
    def __init__(self, *args, **kwargs):
        #print "test: ", ImagePublication.image.rel
        return super(ImagePublicationForm, self).__init__(*args, **kwargs)
        #self.fields['image'].widget = ForeignKeyRawIdWidget('Image')