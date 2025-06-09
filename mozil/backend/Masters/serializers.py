
from .models import *
from rest_framework import serializers

class RegionMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= RegionMaster
        fields='__all__'
