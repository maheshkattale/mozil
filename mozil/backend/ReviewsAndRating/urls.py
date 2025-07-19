from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('service_provider_reviews_and_rating_list_pagination_api', service_provider_reviews_and_rating_list_pagination_api.as_view(), name = 'service_provider_reviews_and_rating_list_pagination_api'),
    path('reviews_and_rating_list_pagination_api', reviews_and_rating_list_pagination_api.as_view(), name = 'reviews_and_rating_list_pagination_api'),
    path('service_provider_reviews_and_rating_list', service_provider_reviews_and_rating_list.as_view(), name = 'service_provider_reviews_and_rating_list'),
    path('addreviews_and_rating', addreviews_and_rating.as_view(), name = 'addreviews_and_rating'),
    path('reviews_and_ratingdelete', reviews_and_ratingdelete.as_view(), name = 'reviews_and_ratingdelete'),
    path('reviews_and_ratingbyid', reviews_and_ratingbyid.as_view(), name = 'reviews_and_ratingbyid'),
    path('updatereviews_and_rating', updatereviews_and_rating.as_view(), name = 'updatereviews_and_rating'),
    path('user_submited_reviews_and_rating_list', user_submited_reviews_and_rating_list.as_view(), name = 'user_submited_reviews_and_rating_list'),
    path('user_submited_reviews_and_rating_list_pagination_api', user_submited_reviews_and_rating_list_pagination_api.as_view(), name = 'user_submited_reviews_and_rating_list_pagination_api'),

]