from django.shortcuts import render, redirect, HttpResponse,HttpResponseRedirect
import requests
import os
import json
from datetime import datetime,date,timedelta
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import datetime
from datetime import date
# from project.views import statuscheck
from rest_framework.response import Response
from helpers.validations import hosturl



# from Users.context_processers import ImageURL as imageURL
login_url=hosturl+"/api/User/login"
logout_url=hosturl+"/api/User/logout"
forgot_password_url=hosturl+"/api/User/forgot_password"
get_parent_services_list_url=hosturl+"/api/Services/parentservicelist"
get_child_services_list_url=hosturl+"/api/Services/childservicelist"
add_service_provider_url=hosturl+"/api/User/create_new_service_provider"
get_service_provider_details_url=hosturl+"/api/User/get_service_provider_details"
edit_service_provider_url=hosturl+"/api/User/update_service_provider_basic_details"


# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        data = {}
        data['email'] = email
        data['password'] = password
        data['source'] = 'Mobile'

        login_request = requests.post(login_url, data=data)
        login_response = login_request.json()
        print("login_response",login_response)
        if login_response['response']['n'] == 1:
            token = login_response['data']['token']
            request.session['token'] = token 
            request.session['role_id'] = login_response['data']['role'] 
            request.session['role_name'] = login_response['data']['role_name']  
            request.session['user_name'] = login_response['data']['username']   
            return HttpResponse(json.dumps(login_response),content_type='application/json')
        else:
            # messages.error(request, login_response['response']['msg'])
            return HttpResponse(json.dumps(login_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_login_basic.html')

def logout(request):
    if request.method == 'POST':
        token = request.session.get('token')
        headers = {'Authorization': f'Bearer {token}'}
        logout_request = requests.post(logout_url,headers=headers)
        logout_response = logout_request.json()
        if logout_response['response']['n'] == 1:
            del request.session['token']
            return HttpResponse(json.dumps(logout_response),content_type='application/json')
        else:
            return HttpResponse(json.dumps(logout_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_login_basic.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        data = {}
        data['email'] = email
        data['source'] = 'Mobile'

        forgot_password_request = requests.post(forgot_password_url, data=data)
        forgot_password_response = forgot_password_request.json()

        if forgot_password_response['response']['n'] == 1:
 
            return HttpResponse(json.dumps(forgot_password_response),content_type='application/json')
        else:
            # messages.error(request, forgot_password_response['response']['msg'])
            return HttpResponse(json.dumps(forgot_password_response),content_type='application/json')
    else:
        return render(request, 'Authentication/auth_forgot_password_basic.html')


def service_provider_master(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'ServiceProvider/service_provider_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

def add_service_provider(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_service_provider_request = requests.post(add_service_provider_url, data=data,headers=headers,files=request.FILES)
            add_service_provider_response = add_service_provider_request.json()
            return HttpResponse(json.dumps(add_service_provider_response),content_type='application/json')
        else:
            get_parent_service_request = requests.get(get_parent_services_list_url,headers=headers)
            get_parent_service_response = get_parent_service_request.json()
            get_child_service_request = requests.get(get_child_services_list_url,headers=headers)
            get_child_service_response = get_child_service_request.json()

            return render(request, 'ServiceProvider/add_service_provider.html',{'parent_services':get_parent_service_response['data'],'child_services':get_child_service_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

def edit_service_provider(request,id):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_service_provider_request = requests.post(edit_service_provider_url, data=data,headers=headers,files=request.FILES)
            edit_service_provider_response = edit_service_provider_request.json()
            return HttpResponse(json.dumps(edit_service_provider_response),content_type='application/json')
        else:
            data={'service_provider_id':id}
            get_parent_service_request = requests.get(get_parent_services_list_url,headers=headers)
            get_parent_service_response = get_parent_service_request.json()
            get_child_service_request = requests.get(get_child_services_list_url,headers=headers)
            get_child_service_response = get_child_service_request.json()
            get_service_provider_details_request = requests.post(get_service_provider_details_url,data=data,headers=headers)
            get_service_provider_details_response = get_service_provider_details_request.json()
            return render(request, 'ServiceProvider/edit_service_provider.html',{'parent_services':get_parent_service_response['data'],'child_services':get_child_service_response['data'],'obj':get_service_provider_details_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.



def service_provider_verification(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Verification/service_provider_verification.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.




def users_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Users/users_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    









