from django.conf.urls.defaults import *

urlpatterns = patterns('image_filer.views',
    url(r'^directory/(?P<folder_id>\d+)/$', 'directory_listing', name='image_filer-directory_listing'),
    url(r'^directory/$', 'directory_listing', name='image_filer-directory_listing-root'),
    url(r'^directory/(?P<folder_id>\d+)/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_folder'),
    url(r'^directory/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_root_folder'),
    
    url(r'^directory/(?P<folder_id>\d+)/upload/$', 'upload', name='image_filer-upload'),
    url(r'^directory/upload/$', 'upload', name='image_filer-upload'),
    
    url(r'^bucket/(?P<bucket_id>\d+)/move_to_folder/$', 'move_files_to_folder', name='image_filer-move_bucket_to_folder'),
    url(r'^file/move_to_folder/$', 'move_files_to_folder', name='image_filer-move_files_to_folder'),

)
