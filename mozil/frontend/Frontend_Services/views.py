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
add_parent_service_url=hosturl+"/api/Services/addparentservice"
edit_parent_service_url=hosturl+"/api/Services/parentserviceupdate"
get_parent_service_url=hosturl+"/api/Services/parentservicebyid"
get_parent_services_list_url=hosturl+"/api/Services/parentservicelist"

# Create your views here.
def parent_services_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Services/parent/parent_services_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

def add_parent_services(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_parent_service_request = requests.post(add_parent_service_url, data=data,headers=headers,files=request.FILES)
            add_parent_service_response = add_parent_service_request.json()
            return HttpResponse(json.dumps(add_parent_service_response),content_type='application/json')
        else:
            return render(request, 'Services/parent/add_parent_services.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def edit_parent_service(request,id):

    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_parent_service_request = requests.post(edit_parent_service_url, data=data,headers=headers,files=request.FILES)
            edit_parent_service_response = edit_parent_service_request.json()
            return HttpResponse(json.dumps(edit_parent_service_response),content_type='application/json')
        else:
            data={'parentserviceid':id}
            get_parent_service_request = requests.post(get_parent_service_url, data=data,headers=headers,)
            get_parent_service_response = get_parent_service_request.json()
            return render(request, 'Services/parent/edit_parent_services.html',{'parent_service':get_parent_service_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.







add_child_service_url=hosturl+"/api/Services/addchildservice"
edit_child_service_url=hosturl+"/api/Services/childserviceupdate"
get_child_service_url=hosturl+"/api/Services/childservicebyid"

# Create your views here.
def child_services_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Services/child/child_services_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

def add_child_services(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_child_service_request = requests.post(add_child_service_url, data=data,headers=headers,files=request.FILES)
            add_child_service_response = add_child_service_request.json()
            return HttpResponse(json.dumps(add_child_service_response),content_type='application/json')
        else:
            get_parent_service_request = requests.get(get_parent_services_list_url,headers=headers)
            get_parent_service_response = get_parent_service_request.json()
            return render(request, 'Services/child/add_child_services.html',{'parent_services':get_parent_service_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def edit_child_service(request,id):

    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_child_service_request = requests.post(edit_child_service_url, data=data,headers=headers,files=request.FILES)
            edit_child_service_response = edit_child_service_request.json()
            return HttpResponse(json.dumps(edit_child_service_response),content_type='application/json')
        else:
            data={'childserviceid':id}
            get_child_service_request = requests.post(get_child_service_url, data=data,headers=headers,)
            get_child_service_response = get_child_service_request.json()
            get_parent_service_request = requests.get(get_parent_services_list_url,headers=headers)
            get_parent_service_response = get_parent_service_request.json()
            return render(request, 'Services/child/edit_child_services.html',{'child_service':get_child_service_response['data'],'parent_services':get_parent_service_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

















