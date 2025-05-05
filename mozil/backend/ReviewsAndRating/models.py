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
    userid = models.CharField(max_length=250,blank=True,null=True) #rating submited byy
    service_provider_id = models.CharField(max_length=250,blank=True,null=True) #rating submited byy
    status = models.CharField(default="Pending",max_length=250,blank=True,null=True)

class ReviewsAndRatingMedia(TrackingModel):
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    reviews_and_rating_id = models.CharField(max_length=255,null=True, blank=True)
    media = models.FileField(upload_to='reviews_and_rating/media/', blank=True, null=True,verbose_name='media Image')

