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

# Create your views here.
class service_provider_plan_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = PlansSerializer

    def post(self,request):
        plans_objs = ServiceProviderPlanMaster.objects.filter(isActive=True).order_by('-id')
        page4 = self.paginate_queryset(plans_objs)
        serializer = ServiceProviderPlanMasterSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class service_provider_plan_list(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        plans_objs = ServiceProviderPlanMaster.objects.filter(isActive=True).order_by('Name')
        serializer = ServiceProviderPlanMasterSerializer(plans_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Plans found Successfully",
                "status":"success"
                }
        })
    

class addplan(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        print("request.data",request.data)
        data['Name']=str(request.data.get('Name')).lower()
        if data['Name'] is None or data['Name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan name", "status":"error"}})
        
        data['days']=str(request.data.get('days')).lower()
        if data['days'] is None or data['days'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan days", "status":"error"}})
        
        data['amount']=str(request.data.get('amount')).lower()
        if data['amount'] is None or data['amount'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan amount", "status":"error"}})
        
        data['description']=request.data.get('description')

        
        Planexist = ServiceProviderPlanMaster.objects.filter(Name=data['Name'],isActive=True).first()
        if Planexist is None:
            serializer = ServiceProviderPlanMasterSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Plan added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})           
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"plan already exist", "status":"error"}})

class plandelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('plan_id')
        plan_obj = ServiceProviderPlanMaster.objects.filter(id=id,isActive=True).first()
        if plan_obj is not None:
            data['isActive'] = False
            serializer = ServiceProviderPlanMasterSerializer(plan_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Plan deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})

class planbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('plan_id')
        plan_obj = ServiceProviderPlanMaster.objects.filter(id=id,isActive=True).first()
        if plan_obj is not None:
            serializer = ServiceProviderPlanMasterSerializer(plan_obj)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Plan found successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})

class updateplan(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('plan_id')
        data['Name']=str(request.data.get('Name')).lower()
        if data['Name'] is None or data['Name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan name", "status":"error"}})
        
        data['days']=str(request.data.get('days')).lower()
        if data['days'] is None or data['days'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan days", "status":"error"}})
        
        data['amount']=str(request.data.get('amount')).lower()
        if data['amount'] is None or data['amount'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan amount", "status":"error"}})
        
        data['description']=request.data.get('description')



        plan_obj = ServiceProviderPlanMaster.objects.filter(id=id,isActive=True).first()
        if plan_obj is not None:
            serializer = ServiceProviderPlanMasterSerializer(plan_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Plan updated successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})
