# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FileVersion'
        db.create_table('static_management_fileversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('compressed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('static_management', ['FileVersion'])


    def backwards(self, orm):
        
        # Deleting model 'FileVersion'
        db.delete_table('static_management_fileversion')


    models = {
        'static_management.fileversion': {
            'Meta': {'object_name': 'FileVersion'},
            'compressed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'file_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['static_management']
