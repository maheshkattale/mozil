from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('service_provider_plan_list_pagination_api', service_provider_plan_list_pagination_api.as_view(), name = 'service_provider_plan_list_pagination_api'),
    path('service_provider_plan_list', service_provider_plan_list.as_view(), name = 'service_provider_plan_list'),
    path('addplan', addplan.as_view(), name = 'addplan'),
    path('plandelete', plandelete.as_view(), name = 'plandelete'),
    path('planbyid', planbyid.as_view(), name = 'planbyid'),
    path('updateplan', updateplan.as_view(), name = 'updateplan'),

]