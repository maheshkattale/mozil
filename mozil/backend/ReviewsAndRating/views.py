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
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from User.common import CustomPagination
from django.db.models import Q
from django.db.models import Avg
from User.models import *
from User.serializers import *
from django.utils.decorators import method_decorator    
from django.views.decorators.csrf import csrf_exempt




# Create your views here.
class service_provider_reviews_and_rating_list_pagination_api(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = reviews_and_ratingsSerializer

    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        reviews_and_ratings_objs = ReviewsAndRating.objects.filter(service_provider_id=service_provider_id,isActive=True).order_by('-id')
        page4 = self.paginate_queryset(reviews_and_ratings_objs)
        serializer = CustomReviewsAndRatingSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)


class reviews_and_rating_list_pagination_api(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = reviews_and_ratingsSerializer

    def post(self,request):
        reviews_and_ratings_objs = ReviewsAndRating.objects.filter(isActive=True).order_by('-id')
        search = request.data.get('search').strip() if request.data.get('search') else None
        print("reviews_and_ratings_objs",reviews_and_ratings_objs.count())
        if search is not None and search != '':
            reviews_and_ratings_objs = reviews_and_ratings_objs.filter(Q(description__icontains=search) | Q(rating_count__icontains=search)).order_by('-id')

        page4 = self.paginate_queryset(reviews_and_ratings_objs)
        serializer = CustomReviewsAndRatingSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    


class service_provider_reviews_and_rating_list(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        service_provider_id=request.data.get('service_provider_id')

        reviews_and_ratings_objs = ReviewsAndRating.objects.filter(service_provider_id=service_provider_id,isActive=True).order_by('-id')
        serializer = CustomReviewsAndRatingSerializer(reviews_and_ratings_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"reviews and ratings found Successfully",
                "status":"success"
                }
        })
    

class addreviews_and_rating(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        # make_new_average_rating = ReviewsAndRating.objects.filter(isActive__in={True,False}).update(
                # rating_count=0)
        print("request.data",request.data)
        data['description']=str(request.data.get('description')).lower()
        if data['description'] is None or data['description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide reviews description", "status":"error"}})
        
        data['rating_count']=str(request.data.get('rating_count')).lower()
        if data['rating_count'] is None or data['rating_count'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide  rating count", "status":"error"}})
        
        data['service_provider_id']=str(request.data.get('service_provider_id')).lower()
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})
        
        service_provider_obj = ServiceProvider.objects.filter(id=data['service_provider_id'],isActive=True).first()
        if service_provider_obj is None:
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide valid service provider id", "status":"error"}})


        data['userid']=str(request.user.id)

        print("data",data)
        

        serializer = ReviewsAndRatingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            media_list=request.FILES.getlist('media[]')
            for media in media_list:
                d1={
                    "service_provider_id":data['service_provider_id'],
                    "reviews_and_rating_id":serializer.data['id'],
                    "media":media,
                }
                serializer1=ReviewsAndRatingMediaSerializer(data=d1)
                if serializer1.is_valid():
                    serializer1.save()
                else:
                    print("error",serializer1.errors)



            

            avg_rating = ReviewsAndRating.objects.filter(
                service_provider_id=data['service_provider_id'],
                isActive=True
            ).exclude(
                Q(rating_count__isnull=True) 
                # Q(rating_count='') | 
                # Q(rating_count='None')
            ).aggregate(average_rating=Avg('rating_count'))



            print("make_new_average_rating",avg_rating)

            data1={}
            data1['average_rating'] = avg_rating['average_rating']
            serializer2 = ServiceProviderSerializer(service_provider_obj,data=data1,partial=True)
            if serializer2.is_valid():
                serializer2.save()
            else:
                print("error",serializer2.errors)

            return Response({"data" : serializer.data,"response":{"n":1,"msg":"reviews and rating added Successfully!","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})           

class reviews_and_ratingdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('reviews_and_rating_id')
        reviews_and_rating_obj = ReviewsAndRating.objects.filter(id=id,isActive=True).first()
        if reviews_and_rating_obj is not None:
            data['isActive'] = False
            serializer = ReviewsAndRatingSerializer(reviews_and_rating_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()

                reviews_and_rating_media_obj = ReviewsAndRatingMedia.objects.filter(reviews_and_rating_id=id,isActive=True)
                for reviews_and_rating_media in reviews_and_rating_media_obj:
                    data1={}
                    data1['isActive'] = False
                    serializer1 = ReviewsAndRatingMediaSerializer(reviews_and_rating_media,data=data1,partial=True)
                    if serializer1.is_valid():
                        serializer1.save()
                    else:
                        print("error",serializer1.errors)




                make_new_average_rating = ReviewsAndRating.objects.filter(service_provider_id=reviews_and_rating_obj.service_provider_id,isActive=True).aggregate(Avg('rating_count'))
                print("make_new_average_rating",make_new_average_rating)
                service_provider_obj = ServiceProvider.objects.filter(id=reviews_and_rating_obj.service_provider_id,isActive=True).first()
                if service_provider_obj is not None:
                    data1={}
                    data1['average_rating'] = make_new_average_rating['rating_count__avg']
                    serializer2 = ServiceProviderSerializer(service_provider_obj,data=data1,partial=True)
                    if serializer2.is_valid():
                        serializer2.save()
                    else:
                        print("error",serializer2.errors)
                # reviews_and_rating_media_obj.delete()

                return Response({"data":serializer.data,"response": {"n": 1, "msg": "reviews and rating deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "reviews and rating Not Found","status": "error"}})

class reviews_and_ratingbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('reviews_and_rating_id')
        reviews_and_rating_obj = ReviewsAndRating.objects.filter(id=id,isActive=True).first()
        if reviews_and_rating_obj is not None:
            serializer = ReviewsAndRatingSerializer(reviews_and_rating_obj)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "reviews and rating found successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "reviews and rating Not Found","status": "error"}})

class updatereviews_and_rating(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('reviews_and_rating_id')
        data['description']=str(request.data.get('description')).lower()
        if data['description'] is None or data['description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide reviews description", "status":"error"}})
        
        data['rating_count']=str(request.data.get('rating_count')).lower()
        if data['rating_count'] is None or data['rating_count'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide  rating count", "status":"error"}})
        
        data['service_provider_id']=str(request.data.get('service_provider_id')).lower()
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})
        
        data['userid']=str(request.user.id)


        reviews_and_rating_obj = ReviewsAndRating.objects.filter(id=id,isActive=True).first()
        if reviews_and_rating_obj is not None:
            serializer = ReviewsAndRatingSerializer(reviews_and_rating_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()



                media_list=request.FILES.getlist('media[]')
                for media in media_list:
                    d1={
                        "service_provider_id":data['service_provider_id'],
                        "reviews_and_rating_id":serializer.data['id'],
                        "media":media,
                    }
                    serializer1=ReviewsAndRatingMediaSerializer(data=d1)
                    if serializer1.is_valid():
                        serializer1.save()
                    else:
                        print("error",serializer1.errors)

                make_new_average_rating = ReviewsAndRating.objects.filter(service_provider_id=data['service_provider_id'],isActive=True).aggregate(Avg('rating_count'))
                service_provider_obj = ServiceProvider.objects.filter(id=data['service_provider_id'],isActive=True).first()
                if service_provider_obj is not None:
                    data1={}
                    data1['average_rating'] = make_new_average_rating['rating_count__avg']
                    serializer2 = ServiceProviderSerializer(service_provider_obj,data=data1,partial=True)
                    if serializer2.is_valid():
                        serializer2.save()
                    else:
                        print("error",serializer2.errors)

                



                return Response({"data":serializer.data,"response": {"n": 1, "msg": "reviews_and_rating updated successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "reviews and rating Not Found","status": "error"}})


class user_submited_reviews_and_rating_list(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        userid=str(request.user.id)
        reviews_and_ratings_objs = ReviewsAndRating.objects.filter(userid=userid,isActive=True).order_by('-id')
        serializer = CustomReviewsAndRatingSerializer(reviews_and_ratings_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"reviews and ratings found Successfully",
                "status":"success"
                }
        })
    
# Create your views here.
class user_submited_reviews_and_rating_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    # serializer_class = reviews_and_ratingsSerializer

    def post(self,request):
        userid=str(request.user.id)
        reviews_and_ratings_objs = ReviewsAndRating.objects.filter(userid=userid,isActive=True).order_by('-id')
        page4 = self.paginate_queryset(reviews_and_ratings_objs)
        serializer = CustomReviewsAndRatingSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)







