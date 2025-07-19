from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q
from datetime import datetime

# Create your views here.
class advertisement_list_pagination_api(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = advertisementsSerializer

    def post(self,request):
        advertisements_objs = AdvertisementsMaster.objects.filter(isActive=True).order_by('-id')
        search = request.data.get('search')
        if search is not None and search != '':
            advertisements_objs = advertisements_objs.filter(Q(heading__icontains=search) | Q(short_description__icontains=search)| Q(long_description__icontains=search))
        
        page4 = self.paginate_queryset(advertisements_objs)
        serializer = AdvertisementsMasterSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class advertisement_list(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        advertisements_objs = AdvertisementsMaster.objects.filter(isActive=True).order_by('id')
        serializer = AdvertisementsMasterSerializer(advertisements_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Advertisements found Successfully",
                "status":"success"
                }
        })
    
class active_advertisement_list(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        today = datetime.now().strftime('%Y-%m-%d')  # adjust format if needed

        advertisements_objs = AdvertisementsMaster.objects.filter(
            isActive=True,
            start_date__lte=today,  # start date is less than or equal to today
            end_date__gte=today    # end date is greater than or equal to today
        ).order_by('id')
        search = request.GET.get('search')
        print("search",search)
        if search:
            advertisements_objs = advertisements_objs.filter(
                Q(heading__icontains=search) |
                Q(short_description__icontains=search) |
                Q(long_description__icontains=search)
            )

        serializer = AdvertisementsMasterSerializer(advertisements_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Advertisements found Successfully",
                "status":"success"
                }
        })


class addadvertisement(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        print("request.data",request.data)
        data['heading']=str(request.data.get('heading')).lower()
        if data['heading'] is None or data['heading'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement heading", "status":"error"}})
        
        data['start_date']=str(request.data.get('start_date')).lower()
        if data['start_date'] is None or data['start_date'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement start date", "status":"error"}})
        
        data['end_date']=str(request.data.get('end_date')).lower()
        if data['end_date'] is None or data['end_date'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement end date", "status":"error"}})
        


        # Check if the start date is before the end date
        if data['start_date'] > data['end_date']:
            return Response({ "data":{},"response":{"n":0,"msg":"Start date cannot be after end date", "status":"error"}})
        # Check if the start date is in the past
        today = datetime.now().strftime('%Y-%m-%d')  # adjust format if needed
        if data['start_date'] < today:
            return Response({ "data":{},"response":{"n":0,"msg":"Start date cannot be in the past", "status":"error"}})
        

        media=request.FILES.get('media')       
        if media is not None and media !='' and media !='undefined' :
            data['media']=media 
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement media", "status":"error"}})

        data['action_url']=request.data.get('action_url')
        data['short_description']=request.data.get('short_description')
        data['long_description']=request.data.get('long_description')

        
        advertisementexist = AdvertisementsMaster.objects.filter(heading=data['heading'],isActive=True).first()
        if advertisementexist is None:
            serializer = AdvertisementsMasterSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Advertisement added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})           
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Advertisement already exist", "status":"error"}})

class advertisementdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('advertisement_id')
        advertisement_obj = AdvertisementsMaster.objects.filter(id=id,isActive=True).first()
        if advertisement_obj is not None:
            data['isActive'] = False
            serializer = AdvertisementsMasterSerializer(advertisement_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Advertisement deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Advertisement Not Found","status": "error"}})

class advertisementbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('advertisement_id')
        advertisement_obj = AdvertisementsMaster.objects.filter(id=id,isActive=True).first()
        if advertisement_obj is not None:
            serializer = CustomAdvertisementsMasterSerializer(advertisement_obj)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Advertisement found successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Advertisement Not Found","status": "error"}})

class updateadvertisement(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('advertisement_id')
        data['heading']=str(request.data.get('heading')).lower()
        if data['heading'] is None or data['heading'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement heading", "status":"error"}})
        
        data['start_date']=str(request.data.get('start_date')).lower()
        if data['start_date'] is None or data['start_date'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement start date", "status":"error"}})
        
        data['end_date']=str(request.data.get('end_date')).lower()
        if data['end_date'] is None or data['end_date'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide advertisement end date", "status":"error"}})
        
        # Check if the start date is before the end date
        if data['start_date'] > data['end_date']:
            return Response({ "data":{},"response":{"n":0,"msg":"Start date cannot be after end date", "status":"error"}})

        media=request.FILES.get('media')       
        if media is not None and media !='' and media !='undefined' :
            data['media']=media 

        data['action_url']=request.data.get('action_url')
        data['short_description']=request.data.get('short_description')
        data['long_description']=request.data.get('long_description')



        advertisement_obj = AdvertisementsMaster.objects.filter(id=id,isActive=True).first()
        if advertisement_obj is not None:
            serializer = AdvertisementsMasterSerializer(advertisement_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Advertisement updated successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Advertisement Not Found","status": "error"}})
