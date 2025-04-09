
from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= User
        fields='__all__'

class UserlistSerializer(serializers.ModelSerializer):
    role =  serializers.StringRelatedField()
    class Meta:
        model= User
        fields=['id','Username','mobileNumber','email','role']

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model= User
        fields='__all__'
    Role_name = serializers.SerializerMethodField()
    def get_Role_name(self, obj):
        obj_id = obj.role_id
        if obj_id:
            try:
                obj = Role.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.RoleName
                else:
                    return None
            except Role.DoesNotExist:
                return None
        return None
    class Meta:
        model= User
        fields='__all__'


class Roleserializer(serializers.ModelSerializer):
    class Meta:
        model= Role
        fields='__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields ="__all__"


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = "__all__"


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissions
        fields = "__all__"

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields ="__all__"



