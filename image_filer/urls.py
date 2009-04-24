from django.conf.urls.defaults import *

urlpatterns = patterns('image_filer.views',
    url(r'^directory/(?P<folder_id>\d+)/$', 'directory_listing', name='image_filer-directory_listing'),
    url(r'^directory/$', 'directory_listing', name='image_filer-directory_listing-root'),
    url(r'^directory/(?P<folder_id>\d+)/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_folder'),
    url(r'^directory/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_root_folder'),
    
    url(r'^directory/(?P<folder_id>\d+)/upload/$', 'upload', name='image_filer-upload'),
    url(r'^directory/upload/$', 'upload', name='image_filer-upload'),
    
    url(r'^directory/images_with_missing_data/$', 'directory_listing', {'images_with_missing_data': True}, name='image_filer-directory_listing-images_with_missing_data'),

    #url(r'^file/move_to_folder/$', 'move_files_to_folder', name='image_filer-move_files_to_folder'),
    
    url(r'^operations/empty_bucket_in_folder/$', 'empty_bucket_in_folder', name='image_filer-empty_bucket_in_folder'),
    url(r'^operations/clone_files_from_bucket_to_folder/$', 'clone_files_from_bucket_to_folder', name='image_filer-clone_files_from_bucket_to_folder'),
    url(r'^operations/empty_bucket/$', 'empty_bucket', name='image_filer-empty_bucket'),    
    url(r'^operations/put_file_in_bucket/$', 'put_file_in_bucket', name='image_filer-put_file_in_bucket'),
    
    url(r'^image/(?P<image_id>\d+)/export/$', 'export_image', name='image_filer-export_image'),
)
