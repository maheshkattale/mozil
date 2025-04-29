
from .models import *
from rest_framework import serializers
from Plans.models import *
from Plans.serializers import *

from User.models import *
from User.serializers import *

class ServiceProviderPaymentHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ServiceProviderPaymentHistory
        fields='__all__'

class CustomServiceProviderPaymentHistorySerializer(serializers.ModelSerializer):
    
    plan_name = serializers.SerializerMethodField()
    def get_plan_name(self, obj):
        obj_id = obj.plan_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
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
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderPlanMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.days
                else:
                    return None
            except ServiceProviderPlanMaster.DoesNotExist:
                return None
        return None

    plan_description = serializers.SerializerMethodField()
    def get_plan_description(self, obj):
        obj_id = obj.plan_id
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderPlanMaster.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.description
                else:
                    return None
            except ServiceProviderPlanMaster.DoesNotExist:
                return None
        return None

    service_provider_details = serializers.SerializerMethodField()
    def get_service_provider_details(self, obj):
        obj_id = str(obj.userid)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProvider.objects.filter(userid=obj_id).first()
                print("obj",obj,obj_id)

                if obj is not None:
                   service_provider_serializer = CustomServiceProviderSerializer(obj)
                   return service_provider_serializer.data
                else:
                    return {}
            except ServiceProviderPlanMaster.DoesNotExist:
                return {}
        return {}



    class Meta:
        model= ServiceProviderPaymentHistory
        fields='__all__'







