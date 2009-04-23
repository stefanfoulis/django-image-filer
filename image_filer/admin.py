from django.contrib import admin
from models import Folder, Image, FolderPermission, ImagePermission 
from models import ImageManipulationProfile, ImageManipulationStep, ImageManipulationTemplate
from models import Bucket, BucketItem

admin.site.register([FolderPermission, ImagePermission, ImageManipulationTemplate])


class ImageAdmin(admin.ModelAdmin):
    list_display = ('label','admin_thumbnail', 'has_all_mandatory_data')
    list_per_page = 10
    search_fields = ['name', 'original_filename','default_alt_text','default_caption','usage_restriction_notes','notes']
admin.site.register(Image, ImageAdmin)

class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner',)
    list_per_page = 20
admin.site.register(Folder, FolderAdmin)

class ImageManipulationStepInline(admin.TabularInline):
    model = ImageManipulationStep
class ImageManipulationProfileAdmin(admin.ModelAdmin):
    inlines = [ ImageManipulationStepInline, ]
admin.site.register(ImageManipulationProfile, ImageManipulationProfileAdmin)



class BucketItemInline(admin.TabularInline):
    model = BucketItem
class BucketAdmin(admin.ModelAdmin):
    model = Bucket
    inlines = [ BucketItemInline, ]
admin.site.register(Bucket, BucketAdmin)