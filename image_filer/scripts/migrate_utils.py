from image_filer import models as image_filer_models
from django.utils.encoding import force_unicode

def get_image_instance_for_path(image_path):
    print "  handling %s" % (image_path,)
    relative_file_path = image_path
    # check if this file is already under image_filer control
    image_filer_image, created = image_filer_models.Image.objects.get_or_create(file=relative_file_path)
    print "    image_filer.Image: %s create: %s" % (relative_file_path, created)
    if created:
        # create the missing folders objects if necessary
        crumbs = relative_file_path.split('/')[:-1] # all except the filename
        folders = []
        for crumb in crumbs:
            if len(folders):
                parent = folders[-1]
            else:
                parent = None
            print "      checking for Folder: %s" % crumb
            try:
                newfolder = image_filer_models.Folder.objects.get(name=crumb,parent=parent)
                created = False
            except:
                # this sucks, but we don't have mptt stuff in this context :-(
                newfolder = image_filer_models.Folder(name=crumb,parent=parent)
                created = True
            print "        Folder: %s create: %s" % (newfolder.name, created,)
            if created:
                newfolder.save()
                print u"      added folder %s" % (newfolder,)
            folders.append(newfolder)
        if len(folders):
            folder = folders[-1]
        else:
            folder = None

        # the image was not in image_file before... set the minimal mandatory fields
        image_filer_image.original_filename = relative_file_path.split('/')[-1]
        image_filer_image.folder = folder
        image_filer_image.save()
    return image_filer_image