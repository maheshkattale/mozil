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
from Plans.models import *
from Plans.serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q


# Create your views here.
class purchase_plan(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('plan_id')
        if id is None or id =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide plan id", "status":"error"}})

        plan_obj = ServiceProviderPlanMaster.objects.filter(id=id,isActive=True).first()
        if plan_obj is not None:
            plan_serializer = ServiceProviderPlanMasterSerializer(plan_obj)
            data['amount']=plan_serializer.data['amount']
            data['userid']=str(request.user.id)
            data['plan_id']=plan_serializer.data['id']

            serializer=ServiceProviderPaymentHistorySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Plan purchased successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})


class purchase_plan_history(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        plans_obj = ServiceProviderPaymentHistory.objects.filter(userid=str(request.user.id),isActive=True)
        if plans_obj.exists():
            plan_serializer = CustomServiceProviderPaymentHistorySerializer(plans_obj,many=True)
            return Response({"data":plan_serializer.data,"response": {"n": 1, "msg": "Purchased Plan found successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})


class all_purchase_plan_history(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        amount=request.data.get('amount')
        plans_obj = ServiceProviderPaymentHistory.objects.filter(isActive=True).order_by('-createdAt')
        
        if service_provider_id is not None and service_provider_id !='':
            plans_obj=plans_obj.filter(userid=service_provider_id)
        
        if amount is not None and amount !='':
            plans_obj=plans_obj.filter(amount__icontains=amount)


        if plans_obj.exists():
            plan_serializer = CustomServiceProviderPaymentHistorySerializer(plans_obj,many=True)
            return Response({"data":plan_serializer.data,"response": {"n": 1, "msg": "Purchased Plan found successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Plan Not Found","status": "error"}})