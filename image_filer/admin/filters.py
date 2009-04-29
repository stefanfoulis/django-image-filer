from image_filer.filters import library
from image_filer.filters import BaseFilter, ResizeFilter

print "importing image_filer.admin.filters!"

class AdminThumbnailFilter(BaseFilter):
    identifier = 'admin_thumbnail'
    name = 'Admin Thumbnail'
    def render(self, im):
        print 'rendering AdminThumbnailFilter'
        return ResizeFilter().render(im, size_x=128, size_y=128, crop=True, upscale=True, crop_from='center')
library.register(AdminThumbnailFilter)

class AdminTinyThumbnailFilter(BaseFilter):
    identifier = 'admin_tiny_thumbnail'
    name = 'Admin Tiny Thumbnail'
    def render(self, im):
        print 'rendering AdminTinyThumbnailFilter'
        return ResizeFilter().render(im, size_x=32, size_y=32, crop=True, upscale=True, crop_from='center')
library.register(AdminTinyThumbnailFilter)

class AdminSidebarPreviewFilter(BaseFilter):
    identifier = 'admin_sidebar_preview'
    name = 'Admin Sidebar Preview'
    def render(self, im):
        print 'rendering AdminSidebarPreviewFilter'
        return ResizeFilter().render(im, size_x=250, size_y=100, crop=True, upscale=True, crop_from='center')
library.register(AdminSidebarPreviewFilter)