from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('', v.login, name='login'),
    path('logout', v.logout, name='logout'),
    path('forgot_password', v.forgot_password, name='forgot_password'),

    path('service_provider_master', v.service_provider_master, name='service_provider_master'),
    path('add_service_provider', v.add_service_provider, name='add_service_provider'),
    path('edit_service_provider/<str:id>', v.edit_service_provider, name='edit_service_provider'),


    path('service_provider_verification', v.service_provider_verification, name='service_provider_verification'),



]