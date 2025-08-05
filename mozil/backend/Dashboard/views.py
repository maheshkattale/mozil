from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from Services.models import *
from Services.serializers import *
from User.models import *
from User.serializers import *
from Plans.models import *
from Plans.serializers import *
from Advertisements.models import *
from Advertisements.serializers import *
from ReviewsAndRating.models import *
from ReviewsAndRating.serializers import *

from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from helpers.custom_functions import *
# Create your views here.
class recomended_services_api(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = request.data
        if 'service_id' in data:
            service_id = data['service_id']
            if service_id:
                services = ParentServices.objects.filter(
                    isActive=True,
                    id=service_id,
                    recomended=True,
                ).order_by('-id')
            else:
                services = ParentServices.objects.filter(isActive=True).order_by('-id')
        else:
            services = ParentServices.objects.filter(isActive=True).order_by('-id')



            
        services=services.filter(recomended=True)            
        if services.exists():
            serializer = ParentServicesSerializer(services, many=True)
            for service in serializer.data:
                service['child_services'] = ChildServicesSerializer(
                    ChildServices.objects.filter(ParentServiceId=service['id'], isActive=True), many=True).data   
                


            return Response({"data": serializer.data, "response": {"n": 1, "msg": "Parent services fetched successfully!", "status": "success"}})
        else:
            return Response({"data": [], "response": {"n": 0, "msg": "No parent services found!", "status": "error"}})
        



class dashboard_analytics_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        total_service_providers = ServiceProvider.objects.filter(isActive=True).count()
        unverified_service_providers = ServiceProvider.objects.filter(license_verification_status=False,isActive=True).count()
        profit_loss_statement = '0'  # Placeholder for profit/loss statement, can be calculated based on your business logic
        current_month = datetime.now().month
        current_month_year = datetime.now().year
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_month_year = datetime.now().year if current_month > 1 else datetime.now().year - 1

        previous_month_plans_sales = ServiceProviderPaymentHistory.objects.filter(
            createdAt__month=previous_month,
            createdAt__year=previous_month_year,
            status='success'
        ).annotate(
            numeric_amount=Cast('amount', FloatField())
        ).aggregate(
            total_sales=models.Sum('numeric_amount')
        )['total_sales'] or 0

        current_month_plans_sales=ServiceProviderPaymentHistory.objects.filter(
            createdAt__month=current_month,
            createdAt__year=current_month_year,
            status='success'
        ).annotate(
            numeric_amount=Cast('amount', FloatField())
        ).aggregate(
            total_sales=models.Sum('numeric_amount')
        )['total_sales'] or 0
        if previous_month_plans_sales > 0:
            profit_loss_statement = round(((current_month_plans_sales - previous_month_plans_sales) / previous_month_plans_sales) * 100, 2)
        else:
            if current_month_plans_sales > 0:
                profit_loss_statement = '100+ '
            else:
                profit_loss_statement = 0

        weekly_overview_data = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_sales = ServiceProviderPaymentHistory.objects.filter(
                createdAt__date=date,
                status='success'
            ).annotate(
            numeric_amount=Cast('amount', FloatField())
            ).aggregate(
                total_sales=models.Sum('numeric_amount')
            )['total_sales'] or 0
            weekly_overview_data.append({
                'date': date_str,
                'sales': daily_sales
            })

        current_month_service_providers = ServiceProvider.objects.filter(
            createdAt__month=current_month,
            createdAt__year=current_month_year,
            isActive=True
        ).count()

        current_month_cunsumer_plans_sales = 0


        return Response({
            "total_service_providers": total_service_providers,
            "unverified_service_providers": unverified_service_providers,
            "profit_loss_statement": profit_loss_statement,
            "weekly_overview_data": weekly_overview_data,
            "current_month_total_plans_sales": format_indian_rupees(current_month_plans_sales+current_month_cunsumer_plans_sales),
            "previous_month_plans_sales": previous_month_plans_sales,
            "current_month_cunsumer_plans_sales": format_indian_rupees(current_month_cunsumer_plans_sales),
            "current_month_service_provider_plans_sales": format_indian_rupees(current_month_plans_sales),


        })  
    




















