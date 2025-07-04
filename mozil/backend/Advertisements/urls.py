from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('advertisement_list_pagination_api', advertisement_list_pagination_api.as_view(), name = 'advertisement_list_pagination_api'),
    path('advertisement_list', advertisement_list.as_view(), name = 'advertisement_list'),
    path('addadvertisement', addadvertisement.as_view(), name = 'addadvertisement'),
    path('advertisementdelete', advertisementdelete.as_view(), name = 'advertisementdelete'),
    path('advertisementbyid', advertisementbyid.as_view(), name = 'advertisementbyid'),
    path('updateadvertisement', updateadvertisement.as_view(), name = 'updateadvertisement'),


]