from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('region_list_pagination_api', region_list_pagination_api.as_view(), name = 'region_list_pagination_api'),
    path('region_list', region_list.as_view(), name = 'region_list'),
    # path('addregion', addregion.as_view(), name = 'addregion'),
    # path('regiondelete', regiondelete.as_view(), name = 'regiondelete'),
    # path('regionbyid', regionbyid.as_view(), name = 'regionbyid'),
    # path('updateregion', updateregion.as_view(), name = 'updateregion'),

]