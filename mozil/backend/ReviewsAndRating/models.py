from django.db import models
# Create your models here.
from helpers.models import TrackingModel
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE
# Create your models here.


class ReviewsAndRating(TrackingModel):
    rating_count = models.CharField(max_length=250,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    userid = models.CharField(max_length=250,blank=True,null=True)
    status = models.CharField(default="Pending",max_length=250,blank=True,null=True)


