
from .models import *
from rest_framework import serializers

class ReviewsAndRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ReviewsAndRating
        fields='__all__'
