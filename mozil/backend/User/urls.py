from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    #authentication
    path('login', login.as_view(), name = 'login'),
    path('logout', logout.as_view(), name = 'logout'),
    path('changepassword', ChangePassword.as_view(), name = 'changepassword'),
    path('forgetpasswordmail', forgetpasswordmail.as_view(), name = 'forgetpasswordmail'),
    path('setnewpassword', setnewpassword.as_view(), name = 'setnewpassword'),
    path('resetpassword', resetpassword.as_view(), name = 'resetpassword'),

    #role
    path('role_list_pagination_api', role_list_pagination_api.as_view(), name = 'role_list_pagination_api'),
    path('rolelist', rolelist.as_view(), name = 'rolelist'),
    path('addrole', addrole.as_view(), name = 'addrole'),
    path('roleupdate', roleupdate.as_view(), name = 'roleupdate'),
    path('roledelete', roledelete.as_view(), name = 'roledelete'),
    path('rolebyid', rolebyid.as_view(), name = 'rolebyid'),


    #menu
    path('menu-list',Menulist.as_view()),
    path('data-permission',GetPermissionData.as_view()),
    path('User-data-permission',GetUserPermissionData.as_view()),
    

    #user
    path('createuser', createuser.as_view(), name = 'createuser'),
    path('user_list_pagination_api', user_list_pagination_api.as_view(), name = 'user_list_pagination_api'),
    path('userlist', userlist.as_view(), name = 'userlist'),
    path('userupdate', userupdate.as_view(), name = 'userupdate'),
    path('userdelete', userdelete.as_view(), name = 'userdelete'),
    path('userdeleteundo', userdeleteundo.as_view(), name = 'userdeleteundo'),
    path('userbyid', userbyid.as_view(), name = 'userbyid'),

    path('create_new_service_provider', create_new_service_provider.as_view(), name = 'create_new_service_provider'),
    path('update_service_provider_basic_details', update_service_provider_basic_details.as_view(), name = 'update_service_provider_basic_details'),
    path('service_provider_list_pagination_api', service_provider_list_pagination_api.as_view(), name = 'service_provider_list_pagination_api'),
    path('serviceproviderdelete', serviceproviderdelete.as_view(), name = 'serviceproviderdelete'),
    path('get_service_provider_details', get_service_provider_details.as_view(), name = 'get_service_provider_details'),
    path('serviceproviderdeleteonly', serviceproviderdeleteonly.as_view(), name = 'serviceproviderdeleteonly'),

    path('service_provider_weekly_schedule_pagination_api', service_provider_weekly_schedule_pagination_api.as_view(), name = 'service_provider_weekly_schedule_pagination_api'),
    path('add_service_provider_weekly_schedule', add_service_provider_weekly_schedule.as_view(), name = 'add_service_provider_weekly_schedule'),
    path('update_service_provider_weekly_schedule', update_service_provider_weekly_schedule.as_view(), name = 'update_service_provider_weekly_schedule'),
    path('delete_service_provider_weekly_schedule', delete_service_provider_weekly_schedule.as_view(), name = 'delete_service_provider_weekly_schedule'),
    path('get_service_provider_weekly_schedule_by_id', get_service_provider_weekly_schedule_by_id.as_view(), name = 'get_service_provider_weekly_schedule_by_id'),

    path('service_provider_offered_service_pagination_api', service_provider_offered_service_pagination_api.as_view(), name = 'service_provider_offered_service_pagination_api'),
    path('add_service_provider_offered_service', add_service_provider_offered_service.as_view(), name = 'add_service_provider_offered_service'),
    path('update_service_provider_offered_service', update_service_provider_offered_service.as_view(), name = 'update_service_provider_offered_service'),
    path('delete_service_provider_offered_service', delete_service_provider_offered_service.as_view(), name = 'delete_service_provider_offered_service'),
    path('get_service_provider_offered_service_by_id', get_service_provider_offered_service_by_id.as_view(), name = 'get_service_provider_offered_service_by_id'),
    path('service_provider_offered_service', service_provider_offered_service.as_view(), name = 'service_provider_offered_service'),


    path('get_service_provider_highlights', get_service_provider_highlights.as_view(), name = 'get_service_provider_highlights'),
    path('add_service_provider_highlight', add_service_provider_highlight.as_view(), name = 'add_service_provider_highlight'),
    path('delete_service_provider_highlight', delete_service_provider_highlight.as_view(), name = 'delete_service_provider_highlight'),
    path('get_service_provider_highlight_by_id', get_service_provider_highlight_by_id.as_view(), name = 'get_service_provider_highlight_by_id'),
    path('edit_service_provider_highlight', edit_service_provider_highlight.as_view(), name = 'edit_service_provider_highlight'),



    path('add_service_provider_portfolio', add_service_provider_portfolio.as_view(), name = 'add_service_provider_portfolio'),
    path('get_service_provider_portfolio', get_service_provider_portfolio.as_view(), name = 'get_service_provider_portfolio'),
    path('delete_service_provider_portfolio', delete_service_provider_portfolio.as_view(), name = 'delete_service_provider_portfolio'),
    path('delete_portfolio_media', delete_portfolio_media.as_view(), name = 'delete_portfolio_media'),
    path('update_service_provider_portfolio', update_service_provider_portfolio.as_view(), name = 'update_service_provider_portfolio'),
    path('get_service_provider_portfolio_by_id', get_service_provider_portfolio_by_id.as_view(), name = 'get_service_provider_portfolio_by_id'),
    
    path('change_verification', change_verification.as_view(), name = 'change_verification'),
    path('change_guarented', change_guarented.as_view(), name = 'change_guarented'),
    path('change_status', change_status.as_view(), name = 'change_status'),
    path('change_user_status', change_user_status.as_view(), name = 'change_user_status'),



    path('check_business_name_availablity', check_business_name_availablity.as_view(), name = 'check_business_name_availablity'),
    path('check_email_availablity', check_email_availablity.as_view(), name = 'check_email_availablity'),
    path('send_verification_otp_mail', send_verification_otp_mail.as_view(), name = 'send_verification_otp_mail'),
    path('ValidateOTP', ValidateOTP.as_view(), name = 'ValidateOTP'),
    path('register_new_service_provider', register_new_service_provider.as_view(), name = 'register_new_service_provider'),
    path('register_new_consumer', register_new_consumer.as_view(), name = 'register_new_consumer'),
    
    
    
    path('service_provider_filter', service_provider_filter.as_view(), name = 'service_provider_filter'),
    path('service_provider_filter_pagination_api', service_provider_filter_pagination_api.as_view(), name = 'service_provider_filter_pagination_api'),
    path('service_finder', service_finder.as_view(), name = 'service_finder'),
    path('view_service_provider_all_details', view_service_provider_all_details.as_view(), name = 'view_service_provider_all_details'),


    path('parent_service_suggestive_search', parent_service_suggestive_search.as_view(), name = 'parent_service_suggestive_search'),
    path('get_service_provider_media_list', get_service_provider_media_list.as_view(), name = 'get_service_provider_media_list'),
    path('top_rated_service_providers', top_rated_service_providers.as_view(), name = 'top_rated_service_providers'),



]