
from .models import *
from rest_framework import serializers

class AdvertisementsMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= AdvertisementsMaster
        fields='__all__'
