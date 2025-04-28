from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('purchase_plan', purchase_plan.as_view(), name = 'purchase_plan'),
    path('purchase_plan_history', purchase_plan_history.as_view(), name = 'purchase_plan_history'),
    path('all_purchase_plan_history', all_purchase_plan_history.as_view(), name = 'all_purchase_plan_history'),

]