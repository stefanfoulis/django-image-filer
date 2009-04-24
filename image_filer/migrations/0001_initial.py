
from south.db import db
from django.db import models
from image_filer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Folder'
        db.create_table('image_filer_folder', (
            ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
            ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ('name', models.CharField(max_length=255)),
            ('parent', models.ForeignKey(orm.Folder, related_name='children', null=True, blank=True)),
            ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('modified_at', models.DateTimeField(auto_now=True)),
            ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
            ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
            ('owner', models.ForeignKey(auth_models.User, related_name='owned_folders', null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('image_filer', ['Folder'])
        
        # Adding model 'FolderPermission'
        db.create_table('image_filer_folderpermission', (
            ('everybody', models.BooleanField(_("everybody"), default=False)),
            ('can_edit', models.BooleanField(_("can edit"), default=True)),
            ('group', models.ForeignKey(auth_models.Group, null=True, verbose_name=_("group"), blank=True)),
            ('can_read', models.BooleanField(_("can read"), default=False)),
            ('user', models.ForeignKey(auth_models.User, null=True, verbose_name=_("user"), blank=True)),
            ('can_add_children', models.BooleanField(_("can add children"), default=True)),
            ('folder', models.ForeignKey(orm.Folder, null=True, blank=True)),
            ('type', models.SmallIntegerField(_('type'), default=0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('image_filer', ['FolderPermission'])
        
        # Adding model 'ImageManipulationProfile'
        db.create_table('image_filer_imagemanipulationprofile', (
            ('description', models.TextField(null=True, blank=True)),
            ('show_in_library', models.BooleanField(default=False)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationProfile'])
        
        # Adding model 'Bucket'
        db.create_table('image_filer_bucket', (
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(auth_models.User, related_name="buckets")),
        ))
        db.send_create_signal('image_filer', ['Bucket'])
        
        # Adding model 'BucketItem'
        db.create_table('image_filer_bucketitem', (
            ('is_checked', models.BooleanField(default=True)),
            ('bucket', models.ForeignKey(orm.Bucket)),
            ('id', models.AutoField(primary_key=True)),
            ('file', models.ForeignKey(orm.Image)),
        ))
        db.send_create_signal('image_filer', ['BucketItem'])
        
        # Adding model 'ImageManipulationStep'
        db.create_table('image_filer_imagemanipulationstep', (
            ('name', models.CharField(max_length=255, null=True, blank=True)),
            ('order', models.IntegerField(default=0)),
            ('template', models.ForeignKey(orm.ImageManipulationProfile, related_name='steps')),
            ('filter_identifier', models.CharField(max_length=255)),
            ('data', models.TextField(null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('description', models.TextField(null=True, blank=True)),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationStep'])
        
        # Adding model 'Image'
        db.create_table('image_filer_image', (
            ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
            ('date_taken', models.DateTimeField(_('date taken'), null=True, editable=False, blank=True)),
            ('can_use_for_teaching', models.BooleanField(default=True)),
            ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
            ('file', models.ImageField(storage=uuid_file_system_storage, width_field='_file_witdh', height_field='_file_height', upload_to='catalogue', blank=True, null=True)),
            ('owner', models.ForeignKey(auth_models.User, related_name='owned_files', null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('_height_field', models.IntegerField(null=True, blank=True)),
            ('author', models.CharField(max_length=255, null=True, blank=True)),
            ('usage_restriction_notes', models.TextField(null=True, blank=True)),
            ('can_use_for_research', models.BooleanField(default=True)),
            ('must_always_publish_copyright', models.BooleanField(default=False)),
            ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
            ('folder', models.ForeignKey(orm.Folder, related_name='image_files', null=True, blank=True)),
            ('has_all_mandatory_data', models.BooleanField(default=False, editable=False)),
            ('default_caption', models.CharField(max_length=255, null=True, blank=True)),
            ('original_filename', models.CharField(max_length=255, null=True, blank=True)),
            ('parent', models.ForeignKey(orm.Image, related_name='children', null=True, blank=True)),
            ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ('name', models.CharField(max_length=255, null=True, blank=True)),
            ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ('manipulation_profile', models.ForeignKey(orm.ImageManipulationProfile, related_name="images", null=True, blank=True)),
            ('notes', models.TextField(null=True, blank=True)),
            ('modified_at', models.DateTimeField(auto_now=True)),
            ('can_use_for_print', models.BooleanField(default=True)),
            ('_width_field', models.IntegerField(null=True, blank=True)),
            ('contact', models.ForeignKey(auth_models.User, related_name='contact_of_files', null=True, blank=True)),
            ('must_always_publish_author_credit', models.BooleanField(default=False)),
            ('default_alt_text', models.CharField(max_length=255, null=True, blank=True)),
            ('can_use_for_private_use', models.BooleanField(default=True)),
            ('can_use_for_web', models.BooleanField(default=True)),
        ))
        db.send_create_signal('image_filer', ['Image'])
        
        # Adding model 'ImageManipulationTemplate'
        db.create_table('image_filer_imagemanipulationtemplate', (
            ('profile', models.ForeignKey(orm.ImageManipulationProfile, related_name='templates')),
            ('description', models.TextField(null=True, blank=True)),
            ('pre_cache', models.BooleanField(_('pre-cache?'), default=False)),
            ('identifier', models.CharField(unique=True, max_length=255)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('image_filer', ['ImageManipulationTemplate'])
        
        # Adding model 'ImagePermission'
        db.create_table('image_filer_imagepermission', (
            ('everybody', models.BooleanField(_("everybody"), default=False)),
            ('can_edit', models.BooleanField(_("can edit"), default=True)),
            ('group', models.ForeignKey(auth_models.Group, null=True, verbose_name=_("group"), blank=True)),
            ('image', models.ForeignKey(orm.Image, null=True, blank=True)),
            ('can_read', models.BooleanField(_("can read"), default=False)),
            ('user', models.ForeignKey(auth_models.User, null=True, verbose_name=_("user"), blank=True)),
            ('can_add_children', models.BooleanField(_("can add children"), default=True)),
            ('type', models.SmallIntegerField(_('type'), default=0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('image_filer', ['ImagePermission'])
        
        # Creating unique_together for [template, order] on ImageManipulationStep.
        db.create_unique('image_filer_imagemanipulationstep', ['template_id', 'order'])
        
        # Creating unique_together for [parent, name] on Folder.
        db.create_unique('image_filer_folder', ['parent_id', 'name'])
        
    
    
    def backwards(self, orm):
        
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
        
        # Deleting unique_together for [template, order] on ImageManipulationStep.
        db.delete_unique('image_filer_imagemanipulationstep', ['template_id', 'order'])
        
        # Deleting unique_together for [parent, name] on Folder.
        db.delete_unique('image_filer_folder', ['parent_id', 'name'])
        
    
    
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
            'folder': ('models.ForeignKey', ['Folder'], {'related_name': "'image_files'", 'null': 'True', 'blank': 'True'}),
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
            'owner': ('models.ForeignKey', ['auth_models.User'], {'related_name': "'owned_files'", 'null': 'True', 'blank': 'True'}),
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
            'files': ('models.ManyToManyField', ['Image'], {'related_name': '"buckets"', 'through': "'BucketItem'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ['auth_models.User'], {'related_name': '"buckets"'})
        },
        'image_filer.bucketitem': {
            'bucket': ('models.ForeignKey', ['Bucket'], {}),
            'file': ('models.ForeignKey', ['Image'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_checked': ('models.BooleanField', [], {'default': 'True'})
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
        }
    }
    
    complete_apps = ['image_filer']
