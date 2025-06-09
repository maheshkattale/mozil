from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class ParentServices(TrackingModel):
    Name = models.CharField(max_length=150,blank=True,null=True)
    Description = models.CharField(max_length=1150,blank=True,null=True)
    icon_image = models.FileField(upload_to='services/parent/icon_image/', blank=True, null=True,verbose_name='icon Image')
    featured_image = models.FileField(upload_to='services/parent/featured_image/', blank=True, null=True,verbose_name='featured Image')
    recomended=models.BooleanField(default=False,blank=True,null=True)

    def __str__(self):
        return self.Name
    
class ChildServices(TrackingModel):
    Name = models.CharField(max_length=150,blank=True,null=True)
    ParentServiceId = models.CharField(max_length=150,blank=True,null=True)
    Description = models.CharField(max_length=1150,blank=True,null=True)
    icon_image = models.FileField(upload_to='services/child/icon_image/', blank=True, null=True,verbose_name='icon Image')


    def __str__(self):
        return self.Name



