
from south.db import db
from django.db import models
from image_filer.models import *

class Migration:
    
    def forwards(self, orm):
        db.rename_table('image_filer_bucket', 'image_filer_clipboard')
        db.rename_table('image_filer_bucketitem', 'image_filer_clipboarditem')
        db.rename_field('image_file_clipboarditem.bucket_id', 'image_file_clipboarditem.clipboard_id',)
        # Changing field 'Image.folder'
        db.alter_column('image_filer_image', 'folder_id', models.ForeignKey(orm.Folder, null=True, blank=True))
        
    
    
    def backwards(self, orm):
        #db.rename_field('image_file_clipboarditem.clipboard_id','image_file_clipboarditem.bucket_id')
        db.rename_table('image_filer_clipboard' ,'image_file_bucket')
        db.rename_table('image_filer_clipboard_item', 'image_file_bucket_item')
        # Changing field 'Image.folder'
        db.alter_column('image_filer_image', 'folder_id', models.ForeignKey(orm.Folder, null=True, blank=True))
        
    
    
    models = {
        'auth.group': {
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
            'file': ('models.ImageField', [], {'storage': 'uuid_file_system_storage', 'width_field': "'_file_witdh'", 'height_field': "'_file_height'", 'upload_to': "'catalogue'", 'blank': 'True', 'null': 'True'}),
            'folder': ('models.ForeignKey', ['"Folder"'], {'related_name': "'%(class)s_files'", 'null': 'True', 'blank': 'True'}),
            'has_all_mandatory_data': ('models.BooleanField', [], {'default': 'False', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'level': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'lft': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'manipulation_profile': ('models.ForeignKey', ["'ImageManipulationProfile'"], {'related_name': '"images"', 'null': 'True', 'blank': 'True'}),
            'modified_at': ('models.DateTimeField', [], {'auto_now': 'True'}),
            'must_always_publish_author_credit': ('models.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('models.BooleanField', [], {'default': 'False'}),
            'name': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'original_filename': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'owned_%(class)ss'", 'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["'self'"], {'related_name': "'children'", 'null': 'True', 'blank': 'True'}),
            'rght': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'tree_id': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'uploaded_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'usage_restriction_notes': ('models.TextField', [], {'null': 'True', 'blank': 'True'})
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
            'folder': ('models.ForeignKey', ['Folder'], {'null': 'True', 'blank': 'True'}),
            'group': ('models.ForeignKey', ['auth_models.Group'], {'null': 'True', 'verbose_name': '_("group")', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'type': ('models.SmallIntegerField', ["_('type')"], {'default': '0'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'null': 'True', 'verbose_name': '_("user")', 'blank': 'True'})
        },
        'image_filer.imagemanipulationprofile': {
            'description': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'show_in_library': ('models.BooleanField', [], {'default': 'False'})
        },
        'image_filer.bucket': {
            '_stub': True,
            'id': 'models.AutoField(primary_key=True)'
        },
        'image_filer.imagemanipulationstep': {
            'Meta': {'ordering': '("order",)', 'unique_together': '(("template","order"),)'},
            'data': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_identifier': ('models.CharField', [], {'max_length': '255'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('models.IntegerField', [], {'default': '0'}),
            'template': ('models.ForeignKey', ['ImageManipulationProfile'], {'related_name': "'steps'"})
        },
        'image_filer.folder': {
            'Meta': {'unique_together': "(('parent','name'),)"},
            'created_at': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'level': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'lft': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'modified_at': ('models.DateTimeField', [], {'auto_now': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'owner': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'owned_folders'", 'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["'self'"], {'related_name': "'children'", 'null': 'True', 'blank': 'True'}),
            'rght': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'tree_id': ('models.PositiveIntegerField', [],{'db_index':True, 'editable':False}),
            'uploaded_at': ('models.DateTimeField', [], {'auto_now_add': 'True'})
        },
        'image_filer.clipboard': {
            'files': ('models.ManyToManyField', ['Image'], {'related_name': '"clipboards"', 'through': "'ClipboardItem'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'related_name': '"clipboards"'})
        },
        'image_filer.imagemanipulationtemplate': {
            'description': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('models.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('models.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pre_cache': ('models.BooleanField', ["_('pre-cache?')"], {'default': 'False'}),
            'profile': ('models.ForeignKey', ['ImageManipulationProfile'], {'related_name': "'templates'"})
        },
        'image_filer.imagepermission': {
            'can_add_children': ('models.BooleanField', ['_("can add children")'], {'default': 'True'}),
            'can_edit': ('models.BooleanField', ['_("can edit")'], {'default': 'True'}),
            'can_read': ('models.BooleanField', ['_("can read")'], {'default': 'False'}),
            'everybody': ('models.BooleanField', ['_("everybody")'], {'default': 'False'}),
            'group': ('models.ForeignKey', ['auth_models.Group'], {'null': 'True', 'verbose_name': '_("group")', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ForeignKey', ['Image'], {'null': 'True', 'blank': 'True'}),
            'type': ('models.SmallIntegerField', ["_('type')"], {'default': '0'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'null': 'True', 'verbose_name': '_("user")', 'blank': 'True'})
        },
        'image_filer.clipboarditem': {
            'clipboard': ('models.ForeignKey', ['Clipboard'], {}),
            'file': ('models.ForeignKey', ['Image'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_checked': ('models.BooleanField', [], {'default': 'True'})
        }
    }
    
    complete_apps = ['image_filer']
