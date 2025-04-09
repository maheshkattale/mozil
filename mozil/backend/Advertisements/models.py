from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class AdvertisementsMaster(TrackingModel):
    heading = models.CharField(max_length=250,blank=True,null=True)
    start_date = models.CharField(max_length=250,blank=True,null=True)
    end_date = models.CharField(max_length=250,blank=True,null=True)
    short_description = models.TextField(blank=True,null=True)
    long_description = models.TextField(blank=True,null=True)
    media = models.FileField(upload_to='advertisement/media/', blank=True, null=True,verbose_name='media Image')
    status = models.CharField(default="Pending",max_length=250,blank=True,null=True)
    
