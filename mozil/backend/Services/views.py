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
class addparentservice(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['Name']=str(request.data.get('Name')).lower()
        data['Description']=request.data.get('Description')

        icon_image=request.FILES.get('icon_image')       
        if icon_image is not None and icon_image !='':
            data['icon_image']=icon_image 


        if data['Name'] is None or data['Name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide parent service name", "status":"error"}})
        
        
        data['createdBy'] = request.session.get('user_id')
        parentserviceexist = ParentServices.objects.filter(Name=data['Name'],isActive=True).first()
        if parentserviceexist is None:
            serializer = ParentServicesSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Parent service added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})           
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Parent service already exist", "status":"error"}})

class parentservicelist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        parentservice_objs = ParentServices.objects.filter(isActive=True).order_by('id')
        serializer = ParentServicesSerializer(parentservice_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Parent services found Successfully",
                "status":"success"
                }
        })
    
class parentservice_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = ParentServicesSerializer

    def post(self,request):
        parentserviceMaster_objs = ParentServices.objects.filter(isActive=True).order_by('-id')
        page4 = self.paginate_queryset(parentserviceMaster_objs)
        serializer = ParentServicesSerializer(page4,many=True)

        return self.get_paginated_response(serializer.data)
    
    
    
class parentserviceupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('parentserviceid')
        result = []
        if 'result' in request.data.keys():
            result = json.loads(request.data.get('result'))
        parentserviceexist = ParentServices.objects.filter(id=id,isActive= True).first()
        if parentserviceexist is not None:
            data['Name']=str(request.data.get('Name')).lower()
            data['Description']=str(request.data.get('Description')).lower()
            # data['updatedBy'] =str(request.user.id)
            if data['Name'] is None or data['Name'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"please provide parent service name", "status":"error"}})
        
            parentserviceindata = ParentServices.objects.filter(Name=data['Name'],isActive= True).exclude(id=id).first()
            if parentserviceindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "Parent service already exist","status": "error"}})
            else:
                icon_image=request.FILES.get('icon_image')       
                if icon_image is not None and icon_image !='' and icon_image !='undefined' :
                    data['icon_image']=icon_image 
                serializer = ParentServicesSerializer(parentserviceexist,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "Parent service updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Parent service not found ","status": "error"}})

class parentservicebyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        id = request.data.get('parentserviceid')
        parentserviceobjects = ParentServices.objects.filter(id=id,isActive=True).first()
        if parentserviceobjects is not None:
            serializer = ParentServicesSerializer(parentserviceobjects)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Parent service data shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Parent service data not found  ","status": "success"}})

class parentservicedelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('parentserviceid')
        existparentservice = ParentServices.objects.filter(id=id,isActive=True).first()
        if existparentservice is not None:
            data['isActive'] = False
            serializer = ParentServicesSerializer(existparentservice,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Parent service deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Parent service Not Found","status": "error"}})

















class addchildservice(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        request_data=request.data.copy()
        data['Name']=str(request.data.get('Name')).lower()
        data['ParentServiceId']=request.data.get('ParentServiceId')
        data['Description']=request.data.get('Description')
        if data['Name'] is None or data['Name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide child service name", "status":"error"}})
        
        if data['ParentServiceId'] is None or data['ParentServiceId'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide  Parent Service Id", "status":"error"}})
        
        icon_image=request.FILES.get('icon_image')       
        if icon_image is not None and icon_image !='' and icon_image !='undefined' :
            data['icon_image']=icon_image 


        data['createdBy'] = request.session.get('user_id')
        childserviceexist = ChildServices.objects.filter(Name=data['Name'],isActive=True).first()
        if childserviceexist is None:
            serializer = ChildServicesSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"child service added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})           
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"child service already exist", "status":"error"}})

class childservicelist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        childservice_objs = ChildServices.objects.filter(isActive=True).order_by('id')
        serializer = ChildServicesSerializer(childservice_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"child services found Successfully",
                "status":"success"
                }
        })
    
class childservice_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        childserviceMaster_objs = ChildServices.objects.filter(isActive=True).order_by('id')
        page4 = self.paginate_queryset(childserviceMaster_objs)
        serializer = CustomChildServicesSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class childserviceupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('childserviceid')
        result = []
        if 'result' in request.data.keys():
            result = json.loads(request.data.get('result'))
        childserviceexist = ChildServices.objects.filter(id=id,isActive= True).first()
        if childserviceexist is not None:
            data['Name']=str(request.data.get('Name')).lower()
            data['ParentServiceId']= request.data.get('ParentServiceId')
            data['Description']= request.data.get('Description')
            # data['updatedBy'] =str(request.user.id)
            if data['Name'] is None or data['Name'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"please provide child service name", "status":"error"}})

            if data['ParentServiceId'] is None or data['ParentServiceId'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"Please provide  Parent Service Id", "status":"error"}})
        
            icon_image=request.FILES.get('icon_image')       
            if icon_image is not None and icon_image !='' and icon_image !='undefined' :
                data['icon_image']=icon_image 


            childserviceindata = ChildServices.objects.filter(Name=data['Name'],isActive= True).exclude(id=id).first()
            if childserviceindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "child service already exist","status": "error"}})
            else:
                serializer = ChildServicesSerializer(childserviceexist,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "child service updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "child service not found ","status": "error"}})

class childservicebyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        id = request.data.get('childserviceid')
        childserviceobjects = ChildServices.objects.filter(id=id,isActive=True).first()
        if childserviceobjects is not None:
            serializer = ChildServicesSerializer(childserviceobjects)

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "child service data shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "child service data not found  ","status": "success"}})

class childservicedelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('childserviceid')
        existchildservice = ChildServices.objects.filter(id=id,isActive=True).first()
        if existchildservice is not None:
            data['isActive'] = False
            serializer = ChildServicesSerializer(existchildservice,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "child service deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "child service Not Found","status": "error"}})
