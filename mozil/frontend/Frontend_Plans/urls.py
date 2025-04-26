from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('plans_list', v.plans_list, name='plans_list'),
    path('add_plan', v.add_plan, name='add_plan'),
    path('edit_plan/<str:id>', v.edit_plan, name='edit_plan'),


]