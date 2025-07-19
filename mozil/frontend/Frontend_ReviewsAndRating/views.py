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
add_reviews_and_rating_url=hosturl+"/api/reviews_and_rating/addreviews_and_rating"
edit_reviews_and_rating_url=hosturl+"/api/reviews_and_rating/updatereviews_and_rating"
get_reviews_and_rating_url=hosturl+"/api/reviews_and_rating/reviews_and_ratingbyid"
get_reviews_and_rating_list_url=hosturl+"/api/reviews_and_rating/reviews_and_ratinglist"

# Create your views here.
def reviews_and_rating_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'ReviewsAndRating/reviews_and_rating_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    

def add_reviews_and_rating(request):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            add_reviews_and_rating_request = requests.post(add_reviews_and_rating_url, data=data,headers=headers,files=request.FILES)
            add_reviews_and_rating_response = add_reviews_and_rating_request.json()
            return HttpResponse(json.dumps(add_reviews_and_rating_response),content_type='application/json')
        else:
            return render(request, 'reviews_and_rating/add_reviews_and_rating.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    
def edit_reviews_and_rating(request,id):
    token = request.session.get('token',False)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        if request.method == 'POST':
            data=request.POST.copy()
            edit_reviews_and_rating_request = requests.post(edit_reviews_and_rating_url, data=data,headers=headers,files=request.FILES)
            edit_reviews_and_rating_response = edit_reviews_and_rating_request.json()
            return HttpResponse(json.dumps(edit_reviews_and_rating_response),content_type='application/json')
        else:
            data={'reviews_and_rating_id':id}
            get_reviews_and_rating_request = requests.post(get_reviews_and_rating_url, data=data,headers=headers,)
            get_reviews_and_rating_response = get_reviews_and_rating_request.json()
            return render(request, 'reviews_and_rating/edit_reviews_and_rating.html',{'reviews_and_rating':get_reviews_and_rating_response['data']})
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.


