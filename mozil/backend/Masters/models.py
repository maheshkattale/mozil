from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class RegionMaster(TrackingModel):
    Name = models.CharField(max_length=250,blank=True,null=True)
    image = models.FileField(upload_to='master/region/images/', blank=True, null=True,verbose_name='region Image')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.Name