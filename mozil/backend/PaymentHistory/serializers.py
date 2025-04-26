
from .models import *
from rest_framework import serializers
from Plans.models import *
from Plans.serializers import *
class ServiceProviderPaymentHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ServiceProviderPaymentHistory
        fields='__all__'

class CustomServiceProviderPaymentHistorySerializer(serializers.ModelSerializer):
    
    plan_name = serializers.SerializerMethodField()
    def get_plan_name(self, obj):
        obj_id = obj.plan_id
        
        if obj_id:
            try:
                obj = ServiceProviderPlanMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.Name
                else:
                    return None
            except ServiceProviderPlanMaster.DoesNotExist:
                return None
        return None

    plan_days = serializers.SerializerMethodField()
    def get_plan_days(self, obj):
        obj_id = obj.plan_id
        
        if obj_id:
            try:
                obj = ServiceProviderPlanMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.days
                else:
                    return None
            except ServiceProviderPlanMaster.DoesNotExist:
                return None
        return None

    plan_days = serializers.SerializerMethodField()
    def get_plan_days(self, obj):
        obj_id = obj.plan_id
        
        if obj_id:
            try:
                obj = ServiceProviderPlanMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.days
                else:
                    return None
            except ServiceProviderPlanMaster.DoesNotExist:
                return None
        return None




    class Meta:
        model= ServiceProviderPaymentHistory
        fields='__all__'







