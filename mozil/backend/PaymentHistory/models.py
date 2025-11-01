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

class PaymentTransaction(models.Model):
    order_id = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    raw_data = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)



class PaymentTransactionErrorLog(models.Model):
    error= models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)