
from .models import *
from rest_framework import serializers
from Services.models import *
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
        if obj_id is not None and obj_id !='' and obj_id !='None':
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
        
class CustomServiceProviderSerializer(serializers.ModelSerializer):

    owner_name = serializers.SerializerMethodField()
    def get_owner_name(self, obj):
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
    
    email = serializers.SerializerMethodField()
    def get_email(self, obj):
        obj_id = str(obj.userid)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = User.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.email
                else:
                    return None
            except User.DoesNotExist:
                return None
        return None
    
    parent_service_name = serializers.SerializerMethodField()
    def get_parent_service_name(self, obj):
        obj_id = str(obj.parent_service)
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
    
    child_service_name = serializers.SerializerMethodField()
    def get_child_service_name(self, obj):
        obj_id = str(obj.child_service)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ChildServices.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.Name
                else:
                    return None
            except ChildServices.DoesNotExist:
                return None
        return None

    offered_services = serializers.SerializerMethodField()
    def get_offered_services(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderOfferedServices.objects.filter(service_provider_id=obj_id,isActive=True)
                if obj.exists():
                   offered_services_serializer=ServiceProviderOfferedServicesSerializer(obj,many=True)
                   return offered_services_serializer.data
                else:
                    return []
            except ServiceProviderOfferedServices.DoesNotExist:
                return []
        return []

    status = serializers.SerializerMethodField()
    def get_status(self, obj):
        obj_id = str(obj.userid)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = User.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.status
                else:
                    return None
            except User.DoesNotExist:
                return None
        return None

    weekly_schedule = serializers.SerializerMethodField()
    def get_weekly_schedule(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderWeeklySchedule.objects.filter(service_provider_id=obj_id,isActive=True)
                if obj.exists():
                   weekly_schedule_serializer=ServiceProviderWeeklyScheduleSerializer(obj,many=True)
                   return weekly_schedule_serializer.data
                else:
                    return []
            except ServiceProviderWeeklySchedule.DoesNotExist:
                return []
        return []


    highlights = serializers.SerializerMethodField()
    def get_highlights(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderHighlights.objects.filter(service_provider_id=obj_id,isActive=True)
                if obj.exists():
                   highlights_serializer=ServiceProviderHighlightsSerializer(obj,many=True)
                   return highlights_serializer.data
                else:
                    return []
            except ServiceProviderHighlights.DoesNotExist:
                return []
        return []

    portfolio = serializers.SerializerMethodField()
    def get_portfolio(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderPortfolio.objects.filter(service_provider_id=obj_id,isActive=True)
                if obj.exists():
                   portfolio_serializer=CustomServiceProviderPortfolioSerializer(obj,many=True)
                   return portfolio_serializer.data
                else:
                    return []
            except ServiceProviderPortfolio.DoesNotExist:
                return []
        return []

    class Meta:
        model = ServiceProvider
        fields ="__all__"

class ServiceProviderWeeklyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderWeeklySchedule
        fields ="__all__"


class ServiceProviderOfferedServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderOfferedServices
        fields ="__all__"

class ServiceProviderHighlightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderHighlights
        fields ="__all__"

class ServiceProviderPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderPortfolio
        fields ="__all__"
class ServiceProviderPortfolioMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderPortfolioMedia
        fields ="__all__"

class CustomServiceProviderPortfolioSerializer(serializers.ModelSerializer):

    media_list = serializers.SerializerMethodField()
    def get_media_list(self, obj):
        obj_id = str(obj.id)
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = ServiceProviderPortfolioMedia.objects.filter(portfolio_id=obj_id,isActive=True)
                if obj.exists():
                   media_serializer=ServiceProviderPortfolioMediaSerializer(obj,many=True)
                   return media_serializer.data
                else:
                    return []
            except ServiceProviderPortfolioMedia.DoesNotExist:
                return []
        return []
    






    class Meta:
        model = ServiceProviderPortfolio
        fields ="__all__"







        