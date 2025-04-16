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


hosturl = "http://127.0.0.1:8000/"


# from Users.context_processers import ImageURL as imageURL
login_url=hosturl+"api/User/login"
# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        data = {}
        data['email'] = email
        data['password'] = password

        login_request = requests.post(login_url, data=data)
        login_response = login_request.json()
        print("login_response",login_response)

 
   

        if login_response['response']['n'] == 1:
            # if login_response.get('token'):
            #     token = login_response['token']
            #     request.session['token'] = token 
            return HttpResponse(login_response)
        else:
            # messages.error(request, login_response['response']['msg'])
            return HttpResponse(login_response)
    else:
        return render(request, 'Authentication/auth_login_basic.html')
