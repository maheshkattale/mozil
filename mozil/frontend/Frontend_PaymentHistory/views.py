from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
import requests
import os
import json
from datetime import datetime,date,timedelta
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import date
from helpers.validations import hosturl
# from project.views import statuscheck




# from Users.context_processers import ImageURL as imageURL
add_plan_url=hosturl+"/api/Plans/addplan"
edit_plan_url=hosturl+"/api/Plans/updateplan"
get_plan_url=hosturl+"/api/Plans/planbyid"
get_plans_list_url=hosturl+"/api/Plans/planlist"

# Create your views here.
def service_provider_purchase_history(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'PaymentHistory/payment_history.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    