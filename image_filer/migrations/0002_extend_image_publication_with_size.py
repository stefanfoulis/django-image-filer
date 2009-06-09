
from south.db import db
from django.db import models
from image_filer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'ImagePublication.height'
        db.add_column('image_filer_imagepublication', 'height', models.PositiveIntegerField(null=True, blank=True))
        
        # Adding field 'ImagePublication.width'
        db.add_column('image_filer_imagepublication', 'width', models.PositiveIntegerField(null=True, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'ImagePublication.height'
        db.delete_column('image_filer_imagepublication', 'height')
        
        # Deleting field 'ImagePublication.width'
        db.delete_column('image_filer_imagepublication', 'width')
        
    
    
    models = {
        'cms.page': {
            'Meta': {'ordering': "('tree_id','lft')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'image_filer.imagepublication': {
            'Meta': {'_bases': ['cms.models.CMSPlugin']},
            'alt_text': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'caption': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'cmsplugin_ptr': ('models.OneToOneField', ["orm['cms.CMSPlugin']"], {}),
            'height': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'image': ('ImageFilerModelImageField', ["orm['image_filer.Image']"], {}),
            'show_author': ('models.BooleanField', [], {'default': 'False'}),
            'show_copyright': ('models.BooleanField', [], {'default': 'False'}),
            'width': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'image_filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent','name'),)"},
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'level': ('models.PositiveIntegerField', [], {}),
            'lft': ('models.PositiveIntegerField', [], {}),
            'modified_at': ('models.DateTimeField', [], {'auto_now': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'owner': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'owned_folders'", 'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["orm['image_filer.Folder']"], {'related_name': "'children'", 'null': 'True', 'blank': 'True'}),
            'rght': ('models.PositiveIntegerField', [], {}),
            'tree_id': ('models.PositiveIntegerField', [], {}),
            'uploaded_at': ('models.DateTimeField', [], {'auto_now_add': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'image_filer.folderpermission': {
            'can_add_children': ('models.BooleanField', ['_("can add children")'], {'default': 'True'}),
            'can_edit': ('models.BooleanField', ['_("can edit")'], {'default': 'True'}),
            'can_read': ('models.BooleanField', ['_("can read")'], {'default': 'False'}),
            'everybody': ('models.BooleanField', ['_("everybody")'], {'default': 'False'}),
            'folder': ('models.ForeignKey', ["orm['image_filer.Folder']"], {'null': 'True', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['auth_models.Group'], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'type': ('models.SmallIntegerField', ["_('type')"], {'default': '0'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'null': 'True', 'blank': 'True'})
        },
        'cms.cmsplugin': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'image_filer.image': {
            '_height_field': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width_field': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'can_use_for_print': ('models.BooleanField', [], {'default': 'True'}),
            'can_use_for_private_use': ('models.BooleanField', [], {'default': 'True'}),
            'can_use_for_research': ('models.BooleanField', [], {'default': 'True'}),
            'can_use_for_teaching': ('models.BooleanField', [], {'default': 'True'}),
            'can_use_for_web': ('models.BooleanField', [], {'default': 'True'}),
            'contact': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'contact_of_files'", 'null': 'True', 'blank': 'True'}),
            'date_taken': ('models.DateTimeField', ["_('date taken')"], {'null': 'True', 'editable': 'False', 'blank': 'True'}),
            'default_alt_text': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('ImageWithThumbnailsField', [], {'width_field': "'_width_field'", 'height_field': "'_height_field'", 'extra_thumbnails': "{'admin_clipboard_icon':{'size':(32,32),'options':['crop','upscale']},'admin_sidebar_preview':{'size':(210,210),'options':['crop',]},'admin_directory_listing_icon':{'size':(48,48),'options':['crop','upscale']},'admin_tiny_icon':{'size':(32,32),'options':['crop','upscale']},}", 'blank': 'True', 'null': 'True', 'thumbnail': "{'size':(50,50)}"}),
            'folder': ('models.ForeignKey', ["orm['image_filer.Folder']"], {'related_name': "'%(class)s_files'", 'null': 'True', 'blank': 'True'}),
            'has_all_mandatory_data': ('models.BooleanField', [], {'default': 'False', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('models.DateTimeField', [], {'auto_now': 'True'}),
            'must_always_publish_author_credit': ('models.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('models.BooleanField', [], {'default': 'False'}),
            'name': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'original_filename': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'owned_%(class)ss'", 'null': 'True', 'blank': 'True'}),
            'uploaded_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'usage_restriction_notes': ('models.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'image_filer.clipboard': {
            'files': ('models.ManyToManyField', ["orm['image_filer.Image']"], {'related_name': '"clipboards"', 'through': "'ClipboardItem'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'related_name': '"clipboards"'})
        },
        'auth.group': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'image_filer.imagepermission': {
            'can_add_children': ('models.BooleanField', ['_("can add children")'], {'default': 'True'}),
            'can_edit': ('models.BooleanField', ['_("can edit")'], {'default': 'True'}),
            'can_read': ('models.BooleanField', ['_("can read")'], {'default': 'False'}),
            'everybody': ('models.BooleanField', ['_("everybody")'], {'default': 'False'}),
            'group': ('models.ForeignKey', ['auth_models.Group'], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ForeignKey', ["orm['image_filer.Image']"], {'null': 'True', 'blank': 'True'}),
            'type': ('models.SmallIntegerField', ["_('type')"], {'default': '0'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'null': 'True', 'blank': 'True'})
        },
        'image_filer.clipboarditem': {
            'clipboard': ('models.ForeignKey', ["orm['image_filer.Clipboard']"], {}),
            'file': ('models.ForeignKey', ["orm['image_filer.Image']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_checked': ('models.BooleanField', [], {'default': 'True'})
        }
    }
    
    complete_apps = ['image_filer']
