from django.db import models
from django.db.models import Q
from datetime import datetime

class FolderManager(models.Manager):    
    def with_bad_metadata(self):
        return self.get_query_set().filter(has_all_mandatory_data=False)