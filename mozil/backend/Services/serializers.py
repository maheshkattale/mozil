
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


class CustomChildServicesSerializer(serializers.ModelSerializer):
    ParentServiceName = serializers.SerializerMethodField()
    def get_ParentServiceName(self, obj):
        obj_id = obj.ParentServiceId
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ParentServices.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.Name
                else:
                    return None
            except ParentServices.DoesNotExist:
                return None
        return None


    class Meta:
        model= ChildServices
        fields='__all__'
class ServiceSearchLogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= ServiceSearchLog
        fields='__all__'









