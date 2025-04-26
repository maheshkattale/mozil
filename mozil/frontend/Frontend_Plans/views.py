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
def plans_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Plans/plans_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    

def add_plan(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_plan_request = requests.post(add_plan_url, data=data,headers=headers,files=request.FILES)
            add_plan_response = add_plan_request.json()
            return HttpResponse(json.dumps(add_plan_response),content_type='application/json')
        else:
            return render(request, 'Plans/add_plan.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def edit_plan(request,id):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_plan_request = requests.post(edit_plan_url, data=data,headers=headers,files=request.FILES)
            edit_plan_response = edit_plan_request.json()
            return HttpResponse(json.dumps(edit_plan_response),content_type='application/json')
        else:
            data={'plan_id':id}
            get_plan_request = requests.post(get_plan_url, data=data,headers=headers,)
            get_plan_response = get_plan_request.json()
            return render(request, 'Plans/edit_plan.html',{'plan':get_plan_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.


