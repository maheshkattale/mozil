
from .models import *
from User.models import *
from rest_framework import serializers

class ReviewsAndRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ReviewsAndRating
        fields='__all__'
class ReviewsAndRatingMediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ReviewsAndRatingMedia
        fields='__all__'

class CustomReviewsAndRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    def get_user_name(self, obj):
        obj_id = str(obj.userid)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = User.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.Username
                else:
                    return None
            except User.DoesNotExist:
                return None
        return None
    
    service_provider_name = serializers.SerializerMethodField()
    def get_service_provider_name(self, obj):
        obj_id = str(obj.service_provider_id)
        if obj_id is not None and obj_id !='' and obj_id !='None' and obj_id !='none':
            try:
                obj = ServiceProvider.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.business_name
                else:
                    return None
            except ServiceProvider.DoesNotExist:
                return None
        return None
    

    media = serializers.SerializerMethodField()
    def get_media(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None' and obj_id !='none':
            try:
                obj = ReviewsAndRatingMedia.objects.filter(reviews_and_rating_id=obj_id,isActive=True)
                if obj.exists():
                   media_serializer=ReviewsAndRatingMediaSerializer(obj,many=True)
                   return media_serializer.data
                else:
                    return []
            except ReviewsAndRatingMedia.DoesNotExist:
                return []
        return []


    class Meta:
        model= ReviewsAndRating
        fields='__all__'