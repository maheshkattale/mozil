"""
URL configuration for mozil project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # backend
    path('api/User/', include('User.urls')),
    path('api/Services/', include('Services.urls')),
    path('api/Plans/', include('Plans.urls')),
    path('api/PaymentHistory/', include('PaymentHistory.urls')),
    
    #frontend
    path('',include(('Frontend_User.urls', 'Frontend_User'),namespace='Frontend_User')),
    path('dashboard/',include(('Frontend_Dashboard.urls', 'Frontend_Dashboard'),namespace='Frontend_Dashboard')),
    path('services/',include(('Frontend_Services.urls', 'Frontend_Services'),namespace='Frontend_Services')),
    path('plan/',include(('Frontend_Plans.urls', 'Frontend_Plans'),namespace='Frontend_Plans')),
    path('payment_history/',include(('Frontend_PaymentHistory.urls', 'Frontend_PaymentHistory'),namespace='Frontend_PaymentHistory')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
