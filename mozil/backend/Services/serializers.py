
from .models import *
from rest_framework import serializers

class ParentServicesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ParentServices
        fields='__all__'

class ChildServicesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ChildServices
        fields='__all__'