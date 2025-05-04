from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('advertisements_list', v.advertisements_list, name='advertisements_list'),
    path('add_advertisement', v.add_advertisement, name='add_advertisement'),
    path('edit_advertisement/<str:id>', v.edit_advertisement, name='edit_advertisement'),


]