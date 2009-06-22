import os
from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# hack to add the media of the image_filer app
IMAGE_FILER_MEDIA_DIR = os.path.abspath( os.path.join(settings.PROJECT_DIR, '../../image_filer/media/image_filer') )
CMS_MEDIA_DIR = os.path.abspath( os.path.join(settings.PROJECT_DIR, '../image_filer_example/src/django-cms-2.0/cms/media/cms') )

urlpatterns = patterns('',
    (r'^media/image_filer/(?P<path>.*)$', 'django.views.static.serve', {'document_root': IMAGE_FILER_MEDIA_DIR, 'show_indexes': True}),
    (r'^media/cms/(?P<path>.*)$', 'django.views.static.serve', {'document_root': CMS_MEDIA_DIR, 'show_indexes': True}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/image_filer/', include('image_filer.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    url(r'^', include('cms.urls')),
)
