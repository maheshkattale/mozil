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
class region_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    # pagination_class = CustomPagination
    # serializer_class = PlansSerializer

    def post(self,request):
        plans_objs = RegionMaster.objects.filter(isActive=True).order_by('-id')
        search = request.data.get('search')
        if search is not None and search != '':
            plans_objs = plans_objs.filter(Q(Name__icontains=search) | Q(description__icontains=search))

        page4 = self.paginate_queryset(plans_objs)
        serializer = RegionMasterSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class region_list(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        plans_objs = RegionMaster.objects.filter(isActive=True).order_by('Name')
        serializer = RegionMasterSerializer(plans_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Plans found Successfully",
                "status":"success"
                }
        })
    