from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class ServiceProviderPaymentHistory(TrackingModel):
    plan_id = models.CharField(max_length=250,blank=True,null=True)
    amount = models.CharField(max_length=250,blank=True,null=True)
    status = models.CharField(max_length=250,blank=True,null=True)
    userid = models.CharField(max_length=250,blank=True,null=True)
    valid_till_date = models.CharField(max_length=250,blank=True,null=True)
    days = models.CharField(max_length=250,blank=True,null=True)
    transaction_id = models.CharField(max_length=250,blank=True,null=True)

