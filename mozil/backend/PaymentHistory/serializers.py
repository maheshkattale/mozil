
from .models import *
from rest_framework import serializers

class ServiceProviderPaymentHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ServiceProviderPaymentHistory
        fields='__all__'
