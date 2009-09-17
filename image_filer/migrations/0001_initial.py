
from south.db import db
from django.db import models
from image_filer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Folder'
        db.create_table('image_filer_folder', (
            ('id', orm['image_filer.Folder:id']),
            ('parent', orm['image_filer.Folder:parent']),
            ('name', orm['image_filer.Folder:name']),
            ('owner', orm['image_filer.Folder:owner']),
            ('uploaded_at', orm['image_filer.Folder:uploaded_at']),
            ('created_at', orm['image_filer.Folder:created_at']),
            ('modified_at', orm['image_filer.Folder:modified_at']),
            ('lft', orm['image_filer.Folder:lft']),
            ('rght', orm['image_filer.Folder:rght']),
            ('tree_id', orm['image_filer.Folder:tree_id']),
            ('level', orm['image_filer.Folder:level']),
        ))
        db.send_create_signal('image_filer', ['Folder'])
        
        # Adding model 'FolderPermission'
        db.create_table('image_filer_folderpermission', (
            ('id', orm['image_filer.FolderPermission:id']),
            ('folder', orm['image_filer.FolderPermission:folder']),
            ('type', orm['image_filer.FolderPermission:type']),
            ('user', orm['image_filer.FolderPermission:user']),
            ('group', orm['image_filer.FolderPermission:group']),
            ('everybody', orm['image_filer.FolderPermission:everybody']),
            ('can_edit', orm['image_filer.FolderPermission:can_edit']),
            ('can_read', orm['image_filer.FolderPermission:can_read']),
            ('can_add_children', orm['image_filer.FolderPermission:can_add_children']),
        ))
        db.send_create_signal('image_filer', ['FolderPermission'])
        
        # Adding model 'ImageManipulationProfile'
        db.create_table('image_filer_imagemanipulationprofile', (
            ('id', orm['image_filer.ImageManipulationProfile:id']),
            ('name', orm['image_filer.ImageManipulationProfile:name']),
            ('description', orm['image_filer.ImageManipulationProfile:description']),
            ('show_in_library', orm['image_filer.ImageManipulationProfile:show_in_library']),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationProfile'])
        
        # Adding model 'Bucket'
        db.create_table('image_filer_bucket', (
            ('id', orm['image_filer.Bucket:id']),
            ('user', orm['image_filer.Bucket:user']),
        ))
        db.send_create_signal('image_filer', ['Bucket'])
        
        # Adding model 'BucketItem'
        db.create_table('image_filer_bucketitem', (
            ('id', orm['image_filer.BucketItem:id']),
            ('file', orm['image_filer.BucketItem:file']),
            ('bucket', orm['image_filer.BucketItem:bucket']),
            ('is_checked', orm['image_filer.BucketItem:is_checked']),
        ))
        db.send_create_signal('image_filer', ['BucketItem'])
        
        # Adding model 'ImageManipulationStep'
        db.create_table('image_filer_imagemanipulationstep', (
            ('id', orm['image_filer.ImageManipulationStep:id']),
            ('template', orm['image_filer.ImageManipulationStep:template']),
            ('filter_identifier', orm['image_filer.ImageManipulationStep:filter_identifier']),
            ('name', orm['image_filer.ImageManipulationStep:name']),
            ('description', orm['image_filer.ImageManipulationStep:description']),
            ('data', orm['image_filer.ImageManipulationStep:data']),
            ('order', orm['image_filer.ImageManipulationStep:order']),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationStep'])
        
        # Adding model 'Image'
        db.create_table('image_filer_image', (
            ('id', orm['image_filer.Image:id']),
            ('original_filename', orm['image_filer.Image:original_filename']),
            ('name', orm['image_filer.Image:name']),
            ('owner', orm['image_filer.Image:owner']),
            ('uploaded_at', orm['image_filer.Image:uploaded_at']),
            ('modified_at', orm['image_filer.Image:modified_at']),
            ('file', orm['image_filer.Image:file']),
            ('_height_field', orm['image_filer.Image:_height_field']),
            ('_width_field', orm['image_filer.Image:_width_field']),
            ('date_taken', orm['image_filer.Image:date_taken']),
            ('manipulation_profile', orm['image_filer.Image:manipulation_profile']),
            ('parent', orm['image_filer.Image:parent']),
            ('folder', orm['image_filer.Image:folder']),
            ('contact', orm['image_filer.Image:contact']),
            ('default_alt_text', orm['image_filer.Image:default_alt_text']),
            ('default_caption', orm['image_filer.Image:default_caption']),
            ('author', orm['image_filer.Image:author']),
            ('must_always_publish_author_credit', orm['image_filer.Image:must_always_publish_author_credit']),
            ('must_always_publish_copyright', orm['image_filer.Image:must_always_publish_copyright']),
            ('can_use_for_web', orm['image_filer.Image:can_use_for_web']),
            ('can_use_for_print', orm['image_filer.Image:can_use_for_print']),
            ('can_use_for_teaching', orm['image_filer.Image:can_use_for_teaching']),
            ('can_use_for_research', orm['image_filer.Image:can_use_for_research']),
            ('can_use_for_private_use', orm['image_filer.Image:can_use_for_private_use']),
            ('usage_restriction_notes', orm['image_filer.Image:usage_restriction_notes']),
            ('notes', orm['image_filer.Image:notes']),
            ('has_all_mandatory_data', orm['image_filer.Image:has_all_mandatory_data']),
            ('lft', orm['image_filer.Image:lft']),
            ('rght', orm['image_filer.Image:rght']),
            ('tree_id', orm['image_filer.Image:tree_id']),
            ('level', orm['image_filer.Image:level']),
        ))
        db.send_create_signal('image_filer', ['Image'])
        
        # Adding model 'ImageManipulationTemplate'
        db.create_table('image_filer_imagemanipulationtemplate', (
            ('id', orm['image_filer.ImageManipulationTemplate:id']),
            ('identifier', orm['image_filer.ImageManipulationTemplate:identifier']),
            ('name', orm['image_filer.ImageManipulationTemplate:name']),
            ('description', orm['image_filer.ImageManipulationTemplate:description']),
            ('profile', orm['image_filer.ImageManipulationTemplate:profile']),
            ('pre_cache', orm['image_filer.ImageManipulationTemplate:pre_cache']),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationTemplate'])
        
        # Adding model 'ImagePermission'
        db.create_table('image_filer_imagepermission', (
            ('id', orm['image_filer.ImagePermission:id']),
            ('image', orm['image_filer.ImagePermission:image']),
            ('type', orm['image_filer.ImagePermission:type']),
            ('user', orm['image_filer.ImagePermission:user']),
            ('group', orm['image_filer.ImagePermission:group']),
            ('everybody', orm['image_filer.ImagePermission:everybody']),
            ('can_edit', orm['image_filer.ImagePermission:can_edit']),
            ('can_read', orm['image_filer.ImagePermission:can_read']),
            ('can_add_children', orm['image_filer.ImagePermission:can_add_children']),
        ))
        db.send_create_signal('image_filer', ['ImagePermission'])
        
        # Creating unique_together for [template, order] on ImageManipulationStep.
        db.create_unique('image_filer_imagemanipulationstep', ['template_id', 'order'])
        
        # Creating unique_together for [parent, name] on Folder.
        db.create_unique('image_filer_folder', ['parent_id', 'name'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [parent, name] on Folder.
        db.delete_unique('image_filer_folder', ['parent_id', 'name'])
        
        # Deleting unique_together for [template, order] on ImageManipulationStep.
        db.delete_unique('image_filer_imagemanipulationstep', ['template_id', 'order'])
        
        # Deleting model 'Folder'
        db.delete_table('image_filer_folder')
        
        # Deleting model 'FolderPermission'
        db.delete_table('image_filer_folderpermission')
        
        # Deleting model 'ImageManipulationProfile'
        db.delete_table('image_filer_imagemanipulationprofile')
        
        # Deleting model 'Bucket'
        db.delete_table('image_filer_bucket')
        
        # Deleting model 'BucketItem'
        db.delete_table('image_filer_bucketitem')
        
        # Deleting model 'ImageManipulationStep'
        db.delete_table('image_filer_imagemanipulationstep')
        
        # Deleting model 'Image'
        db.delete_table('image_filer_image')
        
        # Deleting model 'ImageManipulationTemplate'
        db.delete_table('image_filer_imagemanipulationtemplate')
        
        # Deleting model 'ImagePermission'
        db.delete_table('image_filer_imagepermission')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'image_filer.bucket': {
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['image_filer.Image']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'buckets'", 'to': "orm['auth.User']"})
        },
        'image_filer.bucketitem': {
            'bucket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['image_filer.Bucket']"}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['image_filer.Image']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_checked': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'image_filer.folder': {
            'Meta': {'unique_together': "(('parent', 'name'),)"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_folders'", 'null': 'True', 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['image_filer.Folder']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'image_filer.folderpermission': {
            'can_add_children': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_read': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'everybody': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['image_filer.Folder']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'image_filer.image': {
            '_height_field': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width_field': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'can_use_for_print': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_use_for_private_use': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_use_for_research': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_use_for_teaching': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_use_for_web': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_of_files'", 'null': 'True', 'to': "orm['auth.User']"}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'image_files'", 'null': 'True', 'to': "orm['image_filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'manipulation_profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'images'", 'null': 'True', 'to': "orm['image_filer.ImageManipulationProfile']"}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['image_filer.Image']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'usage_restriction_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'image_filer.imagemanipulationprofile': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'show_in_library': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'image_filer.imagemanipulationstep': {
            'Meta': {'unique_together': "(('template', 'order'),)"},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['image_filer.ImageManipulationProfile']"})
        },
        'image_filer.imagemanipulationtemplate': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pre_cache': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'templates'", 'to': "orm['image_filer.ImageManipulationProfile']"})
        },
        'image_filer.imagepermission': {
            'can_add_children': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'can_read': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'everybody': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['image_filer.Image']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['image_filer']
