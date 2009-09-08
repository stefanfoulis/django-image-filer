from django.conf.urls.defaults import *

urlpatterns = patterns('image_filer.views',
    #url(r'^directory/(?P<folder_id>\d+)/$', 'directory_listing', name='image_filer-directory_listing'),
    #url(r'^directory/$', 'directory_listing', name='image_filer-directory_listing-root'),
    #url(r'^directory/(?P<folder_id>\d+)/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_folder'),
    #url(r'^directory/make_folder/$', 'make_folder', name='image_filer-directory_listing-make_root_folder'),
    
    #url(r'^util/images_with_missing_data/$', 'directory_listing', {'viewtype': 'images_with_missing_data'}, name='image_filer-directory_listing-images_with_missing_data'),
    #url(r'^util/unfiled_images/$', 'directory_listing', {'viewtype': 'unfiled_images'}, name='image_filer-directory_listing-unfiled_images'),

    #url(r'^file/move_to_folder/$', 'move_files_to_folder', name='image_filer-move_files_to_folder'),
    
    #url(r'^operations/paste_clipboard_to_folder/$', 'paste_clipboard_to_folder', name='image_filer-paste_clipboard_to_folder'),
    #url(r'^operations/clone_files_from_clipboard_to_folder/$', 'clone_files_from_clipboard_to_folder', name='image_filer-clone_files_from_clipboard_to_folder'),
    #url(r'^operations/discard_clipboard/$', 'discard_clipboard', name='image_filer-discard_clipboard'),
    #url(r'^operations/delete_clipboard/$', 'delete_clipboard', name='image_filer-delete_clipboard'),    
    #url(r'^operations/move_file_to_clipboard/$', 'move_file_to_clipboard', name='image_filer-move_file_to_clipboard'),
    #url(r'^operations/upload/$', 'ajax_upload', name='image_filer-ajax_upload'),
    
    #url(r'^image/(?P<image_id>\d+)/export/$', 'export_image', name='image_filer-export_image'),
) + patterns('django.views.generic.simple',
    #(r'^folder/$', 'redirect_to',  {'url': '/admin/image_filer/directory/'}),
    #(r'^image/$', 'redirect_to',  {'url': '/admin/image_filer/directory/'})
)
    
