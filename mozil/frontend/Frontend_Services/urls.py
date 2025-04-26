from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('parent_services_list', v.parent_services_list, name='parent_services_list'),
    path('add_parent_services', v.add_parent_services, name='add_parent_services'),
    path('edit_parent_service/<str:id>', v.edit_parent_service, name='edit_parent_service'),

    path('child_services_list', v.child_services_list, name='child_services_list'),
    path('add_child_services', v.add_child_services, name='add_child_services'),
    path('edit_child_service/<str:id>', v.edit_child_service, name='edit_child_service'),
]