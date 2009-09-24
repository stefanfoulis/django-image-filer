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

def migrate_picture_plugin_to_image_filer_publication(plugin_instance):
    if not plugin_instance.plugin_type == 'PicturePlugin':
        return
    from django.db import connection
    cursor = connection.cursor()
    
    instance, plugin = plugin_instance.get_plugin_instance()
    if not instance:
        return
    picture = instance.picture
    attr_map = {
            'cmsplugin_ptr_id'  : str(plugin_instance.id),
            'alt_text'          : u"'%s'" % picture.alt,
            'caption'           : u"'%s'" % picture.longdesc,
            'float'             : u"'%s'" % picture.float,
            'show_author'       : '0',
            'show_copyright'    : '0',
    }
    if picture.page_link_id in ['',None]:
        attr_map['page_link_id'] = 'NULL'
    else:
        attr_map['page_link_id'] = str(picture.page_link_id)
    try:
        image_filer_image = get_image_instance_for_path(force_unicode(picture.image))
        attr_map.update({
            'image_id'          : str(image_filer_image.id),
            'width'             : str(image_filer_image.width),
            'height'            : str(image_filer_image.height),
        })
    except Exception, e:
        print u"missing image! %s" % e
        return
    
    all_keys = ",".join('`%s`'%key for key in attr_map.keys())
    all_values = u",".join(attr_map.values())
    
    QUERY = '''INSERT INTO cmsplugin_filer (%s) VALUES (%s);''' % (all_keys, all_values)
    #print QUERY
    cursor.execute(QUERY)
    QUERY_UPD = "UPDATE cms_cmsplugin SET plugin_type='ImagePlugin' WHERE id=%s" % plugin_instance.id
    #print QUERY_UPD
    cursor.execute(QUERY_UPD)
    QUERY_DEL = 'DELETE FROM cmsplugin_picture WHERE cmsplugin_ptr_id=%s;' % str(plugin_instance.id)
    #print QUERY_DEL
    cursor.execute(QUERY_DEL)

def migrate_all_picture_plugins():
    from cms.models import CMSPlugin
    for plugin in CMSPlugin.objects.filter(plugin_type='PicturePlugin'):
        migrate_picture_plugin_to_image_filer_publication(plugin)