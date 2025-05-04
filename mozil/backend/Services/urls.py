from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('parentservice_list_pagination_api', parentservice_list_pagination_api.as_view(), name = 'parentservice_list_pagination_api'),
    path('parentservicelist', parentservicelist.as_view(), name = 'parentservicelist'),
    path('addparentservice', addparentservice.as_view(), name = 'addparentservice'),
    path('parentserviceupdate', parentserviceupdate.as_view(), name = 'parentserviceupdate'),
    path('parentservicedelete', parentservicedelete.as_view(), name = 'parentservicedelete'),
    path('parentservicebyid', parentservicebyid.as_view(), name = 'parentservicebyid'),

    path('childservice_list_pagination_api', childservice_list_pagination_api.as_view(), name = 'childservice_list_pagination_api'),
    path('childservicelist', childservicelist.as_view(), name = 'childservicelist'),
    path('addchildservice', addchildservice.as_view(), name = 'addchildservice'),
    path('childserviceupdate', childserviceupdate.as_view(), name = 'childserviceupdate'),
    path('childservicedelete', childservicedelete.as_view(), name = 'childservicedelete'),
    path('childservicebyid', childservicebyid.as_view(), name = 'childservicebyid'),

    path('parent_child_service_list', parent_child_service_list.as_view(), name = 'parent_child_service_list'),

]