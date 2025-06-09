from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

        # path('explore_city_api', explore_city_api.as_view(), name = 'explore_city_api'),
        path('recomended_services_api', recomended_services_api.as_view(), name = 'recomended_services_api'),
        path('dashboard_analytics_api', dashboard_analytics_api.as_view(), name = 'dashboard_analytics_api'),

]