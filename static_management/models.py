import os

from django.db import models

class FileVersion(models.Model):
    file_key = models.CharField(max_length=255, unique=True)
    version = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now=True)
    compressed = models.BooleanField()
    
    @property
    def filename(self):
        name, ext = os.path.splitext(self.file_key)
        return "%s.%s%s" % (name, self.version, ext)