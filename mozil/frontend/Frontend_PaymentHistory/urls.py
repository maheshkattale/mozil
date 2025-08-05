from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
# from django.conf.urls import url
urlpatterns = [
    # path('accessDenied',v.accessDenied, name='accessDenied'),
    # path('admin/', admin.site.urls),
    path('service_provider_purchase_history', v.service_provider_purchase_history, name='service_provider_purchase_history'),
    path('pay/', v.payment_page, name='payment_page'),
    path('payment-callback/', v.payment_callback, name='payment_callback'),
    path('payment-success/', v.payment_success, name='payment_success'),

]