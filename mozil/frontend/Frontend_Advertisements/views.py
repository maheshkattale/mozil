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
add_advertisement_url=hosturl+"/api/Advertisements/addadvertisement"
edit_advertisement_url=hosturl+"/api/Advertisements/updateadvertisement"
get_advertisement_url=hosturl+"/api/Advertisements/advertisementbyid"
get_advertisements_list_url=hosturl+"/api/Advertisements/advertisementlist"

# Create your views here.
def advertisements_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Advertisements/advertisements_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    

def add_advertisement(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_advertisement_request = requests.post(add_advertisement_url, data=data,headers=headers,files=request.FILES)
            add_advertisement_response = add_advertisement_request.json()
            return HttpResponse(json.dumps(add_advertisement_response),content_type='application/json')
        else:
            return render(request, 'Advertisements/add_advertisement.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def edit_advertisement(request,id):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_advertisement_request = requests.post(edit_advertisement_url, data=data,headers=headers,files=request.FILES)
            edit_advertisement_response = edit_advertisement_request.json()
            return HttpResponse(json.dumps(edit_advertisement_response),content_type='application/json')
        else:
            data={'advertisement_id':id}
            get_advertisement_request = requests.post(get_advertisement_url, data=data,headers=headers,)
            get_advertisement_response = get_advertisement_request.json()
            return render(request, 'Advertisements/edit_advertisement.html',{'advertisement':get_advertisement_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.


