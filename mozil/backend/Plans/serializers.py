
from .models import *
from rest_framework import serializers

class ServiceProviderPlanMasterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ServiceProviderPlanMaster
        fields='__all__'
