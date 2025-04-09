from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class ServiceProviderPlanMaster(TrackingModel):
    Name = models.CharField(max_length=250,blank=True,null=True)
    days = models.CharField(max_length=250,blank=True,null=True)
    amount = models.CharField(max_length=250,blank=True,null=True)
    
    def __str__(self):
        return self.Name