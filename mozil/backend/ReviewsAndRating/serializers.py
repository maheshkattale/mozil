
from .models import *
from rest_framework import serializers

class ReviewsAndRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ReviewsAndRating
        fields='__all__'
class ReviewsAndRatingMediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ReviewsAndRatingMedia
        fields='__all__'