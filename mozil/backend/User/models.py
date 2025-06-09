from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from helpers.models import TrackingModel
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
import uuid
import jwt
from datetime import datetime, timedelta
from django.db.models.deletion import CASCADE



class Role(TrackingModel):
    RoleName = models.CharField(max_length=150)
    
    def __str__(self):
        return self.RoleName

class UserManager(BaseUserManager):
    def create(self,email,password,**extra_fields):
        if not email:
            raise ValueError("User must have a valid email")
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Username = models.CharField(max_length=255,null=True,blank=True)
    textPassword = models.CharField(max_length=255,null=True,blank=True)
    mobileNumber = models.BigIntegerField(null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,null=True,blank=True)
    source = models.CharField(max_length=255,null=True,blank=True)
    status = models.BooleanField(default=True,null=True,blank=True)
    profile_picture = models.FileField(upload_to='users/profile_picture/', blank=True, null=True,verbose_name='profile_picture Image')
    


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class UserToken(TrackingModel):
    User = models.CharField(max_length=255,null=True, blank=True)
    source = models.CharField(max_length=255,null=True,blank=True)
    WebToken = models.TextField(null=True, blank=True)
    MobileToken = models.TextField(null=True, blank=True)

class Menu(models.Model):
    isActive=models.BooleanField(default=True)
    menuItem=models.CharField(max_length=255)
    menuPath=models.CharField(max_length=255)
    parentId=models.IntegerField(null=True, blank=True)
    subparentId=models.IntegerField(default=0)
    sortOrder=models.IntegerField(null=True, blank=True)
    isshown = models.BooleanField(default=True)

class RolePermissions(TrackingModel):
    role = models.IntegerField(null=True, blank=True)  
    add = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    menu= models.IntegerField(default=0)


class UserPermissions(TrackingModel):
    userid = models.CharField(max_length=255)
    role = models.IntegerField(null=True, blank=True)  
    add = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    menu= models.IntegerField(default=0)


class ServiceProvider(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    parent_service = models.CharField(max_length=255,null=True,blank=True)
    child_service = models.CharField(max_length=255,null=True,blank=True)
    mobile_number = models.CharField(max_length=255,null=True,blank=True)
    alternate_mobile_number = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    lattitude = models.CharField(max_length=255,null=True,blank=True)
    longitude = models.CharField(max_length=255,null=True,blank=True)
    radius = models.CharField(max_length=255,null=True,blank=True)
    license_verification_status = models.BooleanField(default=False,null=True,blank=True)
    mozil_guarented = models.BooleanField(default=False,null=True,blank=True)
    business_logo = models.FileField(upload_to='service_provider/business_logo/', blank=True, null=True,verbose_name='business_logo Image')
    business_name = models.CharField(max_length=255,null=True,blank=True)
    average_rating = models.CharField(max_length=255,null=True,blank=True)
    business_registration_number = models.CharField(max_length=255,null=True,blank=True)
    address = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=255,null=True,blank=True)


class ServiceProviderWeeklySchedule(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    service_start_time = models.CharField(max_length=255,null=True,blank=True)
    service_end_time = models.CharField(max_length=255,null=True,blank=True)
    weekday_name = models.CharField(max_length=255,null=True,blank=True)
    weekday_number = models.CharField(max_length=255,null=True,blank=True)

class ServiceProviderOfferedServices(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    short_description =  models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    rate = models.CharField(max_length=255,null=True,blank=True)
    




class ServiceProviderHighlights(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    name =  models.TextField(null=True, blank=True)
    sticker = models.FileField(upload_to='service_provider/highlights/sticker/', blank=True, null=True,verbose_name='sticker Image')
    description = models.TextField(null=True, blank=True)

class ServiceProviderPortfolio(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    heading =  models.TextField(null=True, blank=True)
    short_description =  models.TextField(null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)

class ServiceProviderPortfolioMedia(TrackingModel):
    userid = models.CharField(max_length=255,null=True, blank=True)
    service_provider_id = models.CharField(max_length=255,null=True, blank=True)
    portfolio_id = models.CharField(max_length=255,null=True, blank=True)
    media = models.FileField(upload_to='service_provider/portfolio/media/', blank=True, null=True,verbose_name='media Image')

# class AddressForm(forms.Form):
#     street_address = forms.CharField(label="Street Address", max_length=255)
#     city = forms.CharField(initial="Moriches", disabled=True)
#     state = forms.CharField(initial="NY", disabled=True)
#     zip_code = forms.ChoiceField(
#         label="ZIP Code",
#         choices=[
#             ('11934', 'Center Moriches'),
#             ('11940', 'East Moriches'),
#             ('11955', 'Moriches'),
#         ]
#     )
#     zip_plus4 = forms.CharField(
#         label="ZIP+4 Code (Optional)",
#         max_length=10,
#         required=False
#     )




class EmailOTPVerification(TrackingModel):
    email = models.CharField(max_length=255,null=True, blank=True)
    otp = models.CharField(max_length=255,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)  