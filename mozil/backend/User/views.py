from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from .jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import make_password,check_password
from .common import CustomPagination
import re
import random
from django.core.mail import send_mail
from django.utils.timezone import make_aware
from django.utils import timezone
from Services.models import *
from Services.serializers import *
from django.db.models import F, FloatField, ExpressionWrapper,Q
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt
from PaymentHistory.views import mark_1_month_free_subscription
import math
from helpers.validations import hosturl
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def createtoken(uuid,email,source):
    token = jwt.encode(
        {'id': uuid,
            'email': email,
            'source':source
           },
        settings.SECRET_KEY, algorithm='HS256')
    return token

class login(GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        Password = request.data.get("password")
        source = request.data.get("source")
        if email is None or Password is None :
            return Response( {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please provide email and password',
                    'n':0
                    }})
        
        userexist = User.objects.filter(email=email, isActive=True).first()
        if userexist is None:
           return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'This user is not found',
                    'n':0
                    }}
                           )
        elif userexist.status == False:
            return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'This account is deactivated',
                    'n':0
                    }}
                           )
        else:
            user_serializer=UserSerializer(userexist)
            p = check_password(Password,userexist.password)
            if p is False:
                return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please enter correct password',
                    'n':0
                    }})
            else:
                useruuid = str(userexist.id)
                username = userexist.Username
                # short_name = ''.join([word[0] for word in username.split()]).upper()

                role =  userexist.role_id
                role_name =  str(userexist.role)
                ifservice_provider=False
                service_provider_details={}



                if role == 2:
                    ifservice_provider=True
                    service_provider_obj=ServiceProvider.objects.filter(userid=useruuid,isActive=True).first()
                    if service_provider_obj is not None:
                        service_provider_serializer=ServiceProviderSerializer(service_provider_obj)
                        service_provider_details=service_provider_serializer.data
                    else:
                        service_provider_details={}
                else:
                    service_provider_details={}



                print("userexist.role",userexist.role)
                
                Token = createtoken(useruuid,email,source)
                
                if source == "Web":
                    web_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createwebtoken = UserToken.objects.create(User=useruuid,WebToken=Token,source=source)
                elif source == "Mobile":
                    mobile_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createmobiletoken = UserToken.objects.create(User=useruuid,MobileToken=Token,source=source)
                else:
                    return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','role':'','role_name':'','Menu':[],'ifservice_provider':False,'email':'','service_provider_details':{}},
                    "response":{
                    "status":"error",
                    'msg': 'Please Provide Source',
                    'n':0
                    }
                })
                
                return Response({
                    "data" : {'token':Token,'username':username,'short_name':'','user_id':useruuid,'role':role,'role_name':role_name,'ifservice_provider':ifservice_provider,'email':email,'service_provider_details':service_provider_details},
                    "response":{
                    "n": 1 ,
                    "msg" : "Login successful",
                    "status":"success"
                    }
                })
            
class logout(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
      
        auth_header = get_authorization_header(request)
        auth_data = auth_header.decode('utf-8')
        auth_token = auth_data.split(" ")
        token = auth_token[1]
        mobiletoken = UserToken.objects.filter(MobileToken=token,isActive=True).update(isActive=False)
        webtoken = UserToken.objects.filter(WebToken=token,isActive=True).update(isActive=False)
        return Response({
                        "data" : '',
                        "response":{
                        "n": 1 ,
                        "msg" : "Logout successful",
                        "status":"success"
                        }
                    })

class ChangePassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        id = request.user.id
        if id is not None:
            userObject = User.objects.filter(id=id,isActive=True,status=True).first()
        
            if userObject:
                password = request.data.get('oldpassword')
                currentPassword = check_password(password,userObject.password)
                if currentPassword==True:
                    newpassword = request.data.get('newpassword')
                
                    confirmpassword = request.data.get('confirmpassword')
                
                    if newpassword==confirmpassword:
                        data['password']= make_password(newpassword)
                        data['textPassword'] = newpassword
                        userSerializer = UserSerializer(userObject,data=data,partial=True)
                        if userSerializer.is_valid():
                            userSerializer.save()

                            tokenfalse = UserToken.objects.filter(User=id,isActive=True).update(isActive=False)
                           
                            return Response({"data":'',"response": {"n": 1, "msg": "Password updated successfully","status": "success"}})
                        else:
                            return Response({"data":'',"response": {"n": 0, "msg": "Password not updated ","status": "error"}})
                    else:
                        return Response({"data":'',"response": {"n": 0, "msg": "New and confirm password not matched ","status": "error"}})
                else:
                    return Response({"data":'',"response": {"n": 0, "msg": "Old password is wrong","status": "error"}})

        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Couldnt find id","status": "error"}})

class forgetpasswordmail(GenericAPIView):
    def post(self,request):
        data={}
        data['email']=request.data.get('email')
        print("request.data",request.data)
        userdata = User.objects.filter(email=data['email'],isActive=True,status=True).first()
        if userdata is not None:
            email =   data['email']
            data2 = {'user_id':userdata.id,'user_email':userdata.email,'frontend_url':hosturl}
            html_mail = render_to_string('mails/reset_password.html',data2)
            
            mailMsg = EmailMessage(
                'Forgot Password?',
                 html_mail,
                'no-reply@zentrotechnologies.com',
                [email],
                )
            mailMsg.content_subtype ="html"
            mailsend = mailMsg.send()
           
            return Response({"data":{},"response":{"n": 1,"msg":"Email Sent Successfully!", "status":"success" }})
        else:
            return Response({"data":{},"response":{"n": 0,"msg" : "User not found", "status":"error"}})

class setnewpassword(GenericAPIView):
    def post(self,request):
        data={}
        data['id']=request.data.get('id')
        empdata = User.objects.filter(id=data['id'],isActive=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                data['PasswordSet'] = True
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password set Successfully!","status":"success"}})
                else:

                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})

class resetpassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['id']=request.data.get('id')
        empdata = User.objects.filter(id=data['id'],isActive=True,PasswordSet=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password Reset Successfully!","status":"success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})
        
#role -----------------------------------------------------------------------------------------------------

class addrole(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['RoleName']=request.data.get('RoleName')
        result = []
        
        if data['RoleName'] is None or data['RoleName'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
        
        
        # request_data['createdBy'] = request.session.get('user_id')
        if 'result' in request_data.keys():
            result = request_data['result']
        roleexist = Role.objects.filter(RoleName=data['RoleName'],isActive=True).first()
        if roleexist is None:
            serializer = Roleserializer(data=data)
            if serializer.is_valid():
                serializer.save()
                for i in result:
                    RolePermissions.objects.create(
                        role = serializer.data['id'],
                        add = i['create'],
                        view = i['read'],
                        edit = i['edit'],
                        delete = i['delete'],
                        menu= i['menu_id']
                    )
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Role added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Role already exist", "status":"error"}})

class rolelist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        role_objs = Role.objects.filter(isActive=True).order_by('id')
        serializer = Roleserializer(role_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Roles found Successfully",
                "status":"success"
                }
        })
    
class role_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def get(self,request):
        RoleMaster_objs = Role.objects.filter(isActive=True).order_by('id')
        page4 = self.paginate_queryset(RoleMaster_objs)
        serializer = Roleserializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class roleupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        result = []
        if 'result' in request.data.keys():
            result = json.loads(request.data.get('result'))
        roleexist = Role.objects.filter(id=id,isActive= True).first()
        if roleexist is not None:
            data['RoleName']=request.data.get('RoleName')
            # data['updatedBy'] =str(request.user.id)
            if data['RoleName'] is None or data['RoleName'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
        
            roleindata = Role.objects.filter(RoleName=data['RoleName'],isActive= True).exclude(id=id).first()
            if roleindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "Role already exist","status": "error"}})
            else:
                serializer = Roleserializer(roleexist,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    RolePermissions.objects.filter(role=serializer.data['id']).delete()
                    for i in result:
                        RolePermissions.objects.create(
                            role = serializer.data['id'],
                            add = i['create'],
                            view = i['read'],
                            edit = i['edit'],
                            delete = i['delete'],
                            menu= i['menu_id']
                        )
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role not found ","status": "error"}})

class rolebyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        id = request.data.get('roleid')
        roleobjects = Role.objects.filter(id=id,isActive=True).first()
        if roleobjects is not None:
            serializer = Roleserializer(roleobjects)
            permission_object = RolePermissions.objects.filter(role= id).order_by("menu")
            permission_ser = PermissionsSerializer(permission_object,many=True)

            serializer_data = serializer.data
            serializer_data.update({
                "permissions":permission_ser.data
            })
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "Role data shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role data not found  ","status": "success"}})

class roledelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        existrole = Role.objects.filter(id=id,isActive=True).first()
        if existrole is not None:
            data['isActive'] = False
            serializer = Roleserializer(existrole,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not Found","status": "error"}})

#user----------------------------------------------------------------------------------------------------

class createuser(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user name", "status":"error"}})
        
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        data['mobileNumber']=request.data.get('mobileNumber')
        if data['mobileNumber'] is None or data['mobileNumber'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})
        
        data['email']=request.data.get('email')
        data['role'] = request.data.get('role')
        data['password'] = data['textPassword']
        data['isActive'] = True
        result = []
        if 'result' in request.data.keys():
            result = request.data.get('result')

        roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
        if roleobj is not None:
            rolename = roleobj.RoleName
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=data['mobileNumber']).first()        
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "Mobile already exist", "status": "error"}})
        
        else:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                userid = serializer.data['id']

                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User registered successfully","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        
class userlist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        empobjects = User.objects.filter(isActive=True).order_by('id')
        serializer = CustomUserSerializer(empobjects, many=True)
        return Response({"data":serializer.data,"response": {"n": 1, "msg": "User list shown successfully","status": "success"}})

class user_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        searchtext = request.data.get("searchtext")
        if searchtext is not None and searchtext != '':
            UserMaster_objs = User.objects.filter(Q(Username__icontains=searchtext,isActive=True)| Q(mobileNumber__icontains =searchtext,isActive=True)).order_by('Username')
        else:
            UserMaster_objs = User.objects.filter(isActive=True).order_by('Username')
        activation_status=request.data.get('activation_status')
        if activation_status is not None and activation_status !='':
            if activation_status == 'true':

                UserMaster_objs = UserMaster_objs.filter(status=True)
            elif activation_status == 'false':

                UserMaster_objs = UserMaster_objs.filter(status=False)     



        page4 = self.paginate_queryset(UserMaster_objs)
        serializer = CustomUserSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)

class userbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        userID = request.data.get("userID")
        empobjects = User.objects.filter(id=userID,isActive=True).first()
        if empobjects is not None:
            serializer = UserSerializer(empobjects)
            serializer_data = serializer.data
            userpermissionobj = UserPermissions.objects.filter(userid=str(userID))
            userser = UserPermissionSerializer(userpermissionobj,many=True)
            serializer_data.update({
                'permissions' : userser.data
            })
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "User shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found  ","status": "success"}})

class userupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userid = request.data.get('userid')
        data['userid'] = request.data.get('userid')
        existemp = User.objects.filter(id=userid,isActive=True).first()
        if existemp is not None:
            data['Username']=request.data.get('Username')
            data['mobileNumber']=request.data.get('mobileNumber')
            mobileNumber = data['mobileNumber']
            data['email']=request.data.get('email')
            email = data['email']
            data['role'] = request.data.get('role')
            data['isActive'] = True
            result = []
            if 'result' in request.data.keys():
                result = json.loads(request.data.get('result'))
            # data['updatedBy'] = str(request.user.id)

            roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
            if roleobj is not None:
                rolename = roleobj.RoleName

            else:
                return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})
            serializer = UserSerializer(existemp,data=data,partial=True)
            emailObject = User.objects.filter(email__in = [email.strip().capitalize(),email.strip(),email.title()],isActive__in=[True]).exclude(id=userid).first()
            mobObject = User.objects.filter(mobileNumber = mobileNumber,isActive__in=[True]).exclude(id=userid).first()
            if emailObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this email id already exist","status": "error"}})
            elif mobObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this mobile number already exist","status": "error"}})
            else:
                if serializer.is_valid():
                    serializer.save()
                    userperm = UserPermissions.objects.filter(userid=data['userid']).delete()
                    for i in result:
                        UserPermissions.objects.create(
                            userid = data['userid'],
                            role =  data['role'],
                            add = i['create'],
                            view = i['read'],
                            edit = i['edit'],
                            delete = i['delete'],
                            menu= i['menu_id']
                        )
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "User updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class userdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=True).first()
        if existemp is not None:
            data['isActive'] = False
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class userdeleteundo(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=False).first()
        if existemp is not None:
            data['isActive'] = True
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User retrived successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})
                
#menu-----------------------------------------------------------------------------------------------
class Menulist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        menuobj=Menu.objects.filter(isActive=True).order_by('sortOrder')
        serializer = MenuSerializer(menuobj,many=True)
        response_={
            'status':'success',
            'msg':'Menu List Found Successfully.',
            'data':serializer.data
        }
        return Response(response_,status=200)
       
class GetPermissionData(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        data['role'] = request.data.get('role')
        roleobj = RolePermissions.objects.filter(role=data['role'], isActive=True).order_by('menu')
        if roleobj is not None:  
            serializer = PermissionsSerializer(roleobj,many=True)
            for i in serializer.data:
                menuobj=Menu.objects.filter(id=i['menu']).first()
                i['menu_path'] = menuobj.menuPath
                i['menu_name'] = menuobj.menuItem
                i['parent_id'] = menuobj.parentId
                i['sub_parent_id'] = menuobj.subparentId
            response_={
                    'status':'success',
                    'msg':'Permission found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'error',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

class GetUserPermissionData(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        data['userid'] = request.data.get('userid')
        userobj = UserPermissions.objects.filter(userid=data['userid'], isActive=True).order_by('menu')
        if userobj is not None:  
            serializer = UserPermissionSerializer(userobj,many=True)
            for i in serializer.data:
                menuobj=Menu.objects.filter(id=i['menu']).first()
                i['menu_path'] = menuobj.menuPath
                i['menu_name'] = menuobj.menuItem
                i['parent_id'] = menuobj.parentId
                i['sub_parent_id'] = menuobj.subparentId
                i['isshown'] = menuobj.isshown


            response_={
                    'status':'success',
                    'msg':'User Permissions found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'error',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

class getmappingusers(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        cclist = []
        # designlist = []
        # operationlist = []
        # budgetinglist = []
        # planninglist = []
        # Auditorlist = []

        ccuserobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='GPL Users')).order_by('id')
        if ccuserobjs.exists():
            ccUserser = UserSerializer(ccuserobjs,many=True)

        
        auditobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='Auditor')).order_by('id')
        if auditobjs.exists():
            auditUserser = UserSerializer(auditobjs,many=True)
            for a in auditUserser.data:
                cclist.append(a)

       


        context = {
            'cclist':cclist,
            # 'designlist':designlist,
            # 'operationlist':operationlist,
            # 'budgetinglist':budgetinglist,
            # 'planninglist':planninglist,
            # 'Auditorlist':Auditorlist
        }
         

        response_={
            'status':'success',
            'msg':'User list found  Successfully.',
            'data':context
        }
        return Response(response_,status=200)
    
class create_new_service_provider(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        if request_data['Username'] is None or request_data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide owner name", "status":"error"}})
        data['Username']=request.data.get('Username')
        data['region']=request.data.get('region')
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        data['mobileNumber']=request.data.get('mobileNumber')
        if data['mobileNumber'] is None or data['mobileNumber'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})
        data['email']=request.data.get('email')
        if data['email'] is None or data['email'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})


        data['password'] = data['textPassword']
        data['isActive'] = True
        data['role'] = 2


        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=data['mobileNumber']).first()        
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "Mobile Number already exist", "status": "error"}})
        else:
            serializer1 = UserSerializer(data=data)
            if serializer1.is_valid():
                data['business_name']=request.data.get('business_name')
                if data['business_name'] is None or data['business_name'] =='':
                    data['business_name']=str(request.data.get('business_name')).lower()
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide business name", "status":"error"}})
                
                data['parent_service']=request.data.get('parent_service')
                if data['parent_service'] is None or data['parent_service'] =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please select parent service", "status":"error"}})
                
                data['child_service']=request.data.get('child_service')
                if data['child_service'] is None or data['child_service'] =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please select child service", "status":"error"}})
                
                data['business_registration_number']=request.data.get('business_registration_number')
                if data['business_registration_number'] is None or data['business_registration_number'] =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide user business registration number", "status":"error"}})
                
                data['mobile_number']= request.data.get('mobileNumber')
                data['alternate_mobile_number'] = request.data.get('alternate_mobile_number')
                data['description'] = request.data.get('description')
                data['website'] = request.data.get('website')
                data['lattitude'] = request.data.get('lattitude')
                data['longitude'] = request.data.get('longitude')
                data['radius'] = request.data.get('radius')

                business_logo = request.FILES.get('business_logo')
                if business_logo is not None and business_logo !='':
                    data['business_logo']=business_logo
                
            
                business_name_obj = ServiceProvider.objects.filter(isActive=True, business_name=data['business_name'].lower()).first()        
                if business_name_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business name already exist", "status": "error"}}) 


                business_registration_number_obj = ServiceProvider.objects.filter(isActive=True, business_registration_number=data['business_registration_number'].lower()).first()        
                if business_registration_number_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business registration number already registered", "status": "error"}})
                        
                else:
                    serializer1.save()
                    userid = serializer1.data['id']
                    data['userid'] = str(userid)

                    serializer2 = ServiceProviderSerializer(data=data)
                    if serializer2.is_valid():
                        serializer2.save()
                        free_subscription = mark_1_month_free_subscription(serializer1.data['id'])
                        if free_subscription:
                            return Response({"data": serializer2.data, "response": {"n": 1, "msg": "Thank you for joining Mozil!\nYour registration is complete and your free plan has been activated for 30 days. Start exploring all the features available to you.", "status": "success"}})


                        return Response({"data":serializer2.data,"response": {"n": 1, "msg": "Service  Provider details registered successfully","status":"success"}})
                    else:
                        first_key, first_value = next(iter(serializer2.errors.items()))
                        return Response({"data" : serializer2.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
            
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        
class serviceproviderdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userid = request.data.get('userid')
        existemp = User.objects.filter(id=str(userid),isActive=True).first()
        if existemp is not None:
            data['isActive'] = False
            serializer1 = UserSerializer(existemp,data=data,partial=True)
            if serializer1.is_valid():
                serializer1.save()
                service_provider_obj = ServiceProvider.objects.filter(isActive=True, userid=str(serializer1.data['id'])).first()        
                if service_provider_obj is not None:
                    service_provider_obj.isActive=False
                    service_provider_obj.save()
                return Response({"data":serializer1.data,"response": {"n": 1, "msg": "Service provider deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class serviceproviderdeleteonly(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        service_provider_id = request.data.get('service_provider_id')
        if service_provider_id is not None and service_provider_id !='':
            service_provider_obj = ServiceProvider.objects.filter(isActive=True, id=service_provider_id).first()        
            if service_provider_obj is not None:
                service_provider_obj.isActive=False
                service_provider_obj.save()
                return Response({"data":[],"response": {"n": 1, "msg": "Service provider deleted successfully","status": "success"}})
            else:
                return Response({"data":'',"response": {"n": 0, "msg": "service provider  not found ","status": "error"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "service provider id not found ","status": "error"}})




class update_service_provider_basic_details(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        service_provider_id=request.data.get('service_provider_id')
        mobileNumber=request.data.get('mobile_number')
        if service_provider_id is None or service_provider_id == '':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        update_obj=ServiceProvider.objects.filter(isActive=True, id=service_provider_id).first()        
        if update_obj is None:
            return Response({ "data":{},"response":{"n":0,"msg":"Service provider not found", "status":"error"}})

        data['Username']=request.data.get('Username')
        data['address']=request.data.get('address')
        data['region']=request.data.get('region')

        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide owner name", "status":"error"}})
        data['Username']=request.data.get('Username')

        
        data['email']=request.data.get('email')
        if data['email'] is None or data['email'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})
        
        
        update_user_obj= User.objects.filter(isActive=True, id=str(update_obj.userid)).first()
        emailobj = User.objects.filter(isActive=True, email=data['email']).exclude(id=str(update_obj.userid)).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=mobileNumber).exclude(id=str(update_obj.userid)).first()        
   
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "Mobile Number already exist", "status": "error"}})
        else:
            serializer1 = UserSerializer(update_user_obj,data=data,partial=True)
            if serializer1.is_valid():
                business_name=request.data.get('business_name')
                if business_name is None or business_name =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide business name", "status":"error"}})
                else:
                    data['business_name']=str(request.data.get('business_name')).lower()

                business_name_obj = ServiceProvider.objects.filter(isActive=True, business_name=data['business_name'].lower()).exclude(id=str(update_obj.id)).first()        
                if business_name_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business name already exist", "status": "error"}}) 

                business_registration_number=request.data.get('business_registration_number')
                if business_registration_number is None or business_registration_number =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide business registration number", "status":"error"}})
                else:
                    data['business_registration_number']=str(request.data.get('business_registration_number')).lower()



                business_registration_number_obj = ServiceProvider.objects.filter(isActive=True, business_registration_number=data['business_registration_number'].lower()).exclude(id=str(update_obj.id)).first()        
                if business_registration_number_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business registration number already exist", "status": "error"}})        
                else:
                    parent_service=request.data.get('parent_service')
                    if parent_service is None or parent_service =='':
                        return Response({ "data":{},"response":{"n":0,"msg":"Please select parent service", "status":"error"}})
                    else:
                        data['parent_service']=parent_service

                    child_service=request.data.get('child_service')
                    if child_service is None or child_service =='':
                        return Response({ "data":{},"response":{"n":0,"msg":"Please select child service", "status":"error"}})
                    else:
                        data['child_service']=child_service

                    data['mobile_number']=request.data.get('mobile_number')
                    data['alternate_mobile_number'] = request.data.get('alternate_mobile_number')
                    data['description'] = request.data.get('description')
                    data['website'] = request.data.get('website')
                    data['lattitude'] = request.data.get('lattitude')
                    data['longitude'] = request.data.get('longitude')
                    data['radius'] = request.data.get('radius')

                    business_logo = request.FILES.get('business_logo')
                    if business_logo is not None and business_logo !='':
                        data['business_logo'] = request.FILES.get('business_logo')

                    data['isActive'] = True
                    
                    serializer = ServiceProviderSerializer(update_obj,data=data,partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        serializer1.save()
                        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Service Provider updated successfully","status":"success"}})
                    else:
                        first_key, first_value = next(iter(serializer.errors.items()))
                        return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class service_provider_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):

        service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('id')
        search=request.data.get("search")
        if search is not None and search != '':
            service_provider_objs = ServiceProvider.objects.filter(Q(business_name__icontains=search,isActive=True)| Q(mobile_number__icontains =search,isActive=True)).order_by('business_name')
        else:
            service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('business_name')
        print("request.data",request.data)
        verification_status= request.data.get("verification_status")
        if verification_status is not None and verification_status != '':
            if verification_status == 'true':
                service_provider_objs = service_provider_objs.filter(license_verification_status=True)
            elif verification_status == 'false':
                service_provider_objs = service_provider_objs.filter(license_verification_status=False)

        guarented_status=request.data.get('guarented_status')
        if guarented_status is not None and guarented_status !='':
            if guarented_status == 'true':
                service_provider_objs = service_provider_objs.filter(mozil_guarented=True)
            elif guarented_status == 'false':
                service_provider_objs = service_provider_objs.filter(mozil_guarented=False)                


        activation_status=request.data.get('activation_status')
        if activation_status is not None and activation_status !='':
            if activation_status == 'true':
                active_service_provider_user_ids=list(User.objects.filter(status=True,role=2).values_list('id',flat=True))

                service_provider_objs = service_provider_objs.filter(userid__in=active_service_provider_user_ids)
            elif activation_status == 'false':
                deactive_service_provider_user_ids=list(User.objects.filter(status=False,role=2).values_list('id',flat=True))

                service_provider_objs = service_provider_objs.filter(userid__in=deactive_service_provider_user_ids)     


        page4 = self.paginate_queryset(service_provider_objs)
        serializer = CustomServiceProviderSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class get_service_provider_details(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        service_provider_id=request.data.get('service_provider_id')
        if service_provider_id is None or service_provider_id == '':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        ServiceProvider_obj=ServiceProvider.objects.filter(isActive=True, id=service_provider_id).first()        
        if ServiceProvider_obj is None:
            return Response({ "data":{},"response":{"n":0,"msg":"Service provider not found", "status":"error"}})

        serializer = ServiceProviderSerializer(ServiceProvider_obj)
        user_obj=User.objects.filter(id=str(serializer.data['userid']),isActive=True).first()
        if user_obj is None:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})

        User_Serializer=UserSerializer(user_obj)
        return Response({"data":{'user':User_Serializer.data,'service_provider':serializer.data},"response": {"n": 1, "msg": "Service provider found successfully","status":"success"}})
       
class service_provider_weekly_schedule_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        service_provider_objs = ServiceProviderWeeklySchedule.objects.filter(service_provider_id=service_provider_id,isActive=True).order_by('id')
        page4 = self.paginate_queryset(service_provider_objs)
        serializer = ServiceProviderWeeklyScheduleSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)

class add_service_provider_weekly_schedule(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()



        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid
        data['weekday_name']=request.data.get('weekday_name')
        if data['weekday_name'] is None or data['weekday_name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide week day name", "status":"error"}})
        
        data['weekday_number']=request.data.get('weekday_number')
        if data['weekday_number'] is None or data['weekday_number'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide week day number", "status":"error"}})
        
        data['service_start_time']=request.data.get('service_start_time')
        if data['service_start_time'] is None or data['service_start_time'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service start time", "status":"error"}})
        
        data['service_end_time']=request.data.get('service_end_time')
        if data['service_end_time'] is None or data['service_end_time'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service end time", "status":"error"}})

        data['isActive'] = True


      

        serializer = ServiceProviderWeeklyScheduleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Weekly schedule added successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class update_service_provider_weekly_schedule(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['weekly_schedule_id']=request.data.get('weekly_schedule_id')
        if data['weekly_schedule_id'] is None or data['weekly_schedule_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide weekly schedule id", "status":"error"}})
        
        update_obj = ServiceProviderWeeklySchedule.objects.filter(isActive=True, id=data['weekly_schedule_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Weekly schedule  not found", "status": "error"}})
        
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid
        data['weekday_name']=request.data.get('weekday_name')
        if data['weekday_name'] is None or data['weekday_name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide week day name", "status":"error"}})
        
        data['weekday_number']=request.data.get('weekday_number')
        if data['weekday_number'] is None or data['weekday_number'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide week day number", "status":"error"}})
        
        data['service_start_time']=request.data.get('service_start_time')
        if data['service_start_time'] is None or data['service_start_time'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service start time", "status":"error"}})
        
        data['service_end_time']=request.data.get('service_end_time')
        if data['service_end_time'] is None or data['service_end_time'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service end time", "status":"error"}})

        data['isActive'] = True


      

        serializer = ServiceProviderWeeklyScheduleSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Weekly schedule updated successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class delete_service_provider_weekly_schedule(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['weekly_schedule_id']=request.data.get('weekly_schedule_id')
        if data['weekly_schedule_id'] is None or data['weekly_schedule_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide weekly schedule id", "status":"error"}})
        
        update_obj = ServiceProviderWeeklySchedule.objects.filter(isActive=True, id=data['weekly_schedule_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Weekly schedule  not found", "status": "error"}})
        

        data['isActive'] = False


      

        serializer = ServiceProviderWeeklyScheduleSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Weekly schedule deleted successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class get_service_provider_weekly_schedule_by_id(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['weekly_schedule_id']=request.data.get('weekly_schedule_id')
        if data['weekly_schedule_id'] is None or data['weekly_schedule_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide weekly schedule id", "status":"error"}})
        
        update_obj = ServiceProviderWeeklySchedule.objects.filter(isActive=True, id=data['weekly_schedule_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Weekly schedule  not found", "status": "error"}})
        



      

        serializer = ServiceProviderWeeklyScheduleSerializer(update_obj)
        

        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Weekly schedule found successfully","status":"success"}})

class register_new_service_provider(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        logined_user_id = str(request.data.get('logined_user_id', ''))

        # if request_data['Username'] is None or request_data['Username'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide owner name", "status":"error"}})
        # data['Username']=request.data.get('Username')

        
        data['Username']=str(request.data.get('Username')).lower()
        data['email']=str(request.data.get('email')).lower()
        if data['email'] is None or data['email'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})


        # data['mobileNumber']=request.data.get('mobileNumber')
        # if data['mobileNumber'] is None or data['mobileNumber'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})

        data['isActive'] = True
        data['role'] = 2


        emailobj = User.objects.filter(isActive=True, email=data['email'])
        if logined_user_id is not None and logined_user_id !='':
            emailobj=emailobj.exclude(id=logined_user_id).first()
        else:
            emailobj=emailobj.first()

        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        else:
            if logined_user_id is not None and logined_user_id !='':
                update_user_obj=User.objects.filter(isActive=True, id=logined_user_id).first()
                if update_user_obj is not None:
                    data['password'] = make_password(data['textPassword'])

                    serializer1 = UserSerializer(update_user_obj,data=data,partial=True)
                else:
                    data['password'] = data['textPassword']

                    serializer1 = UserSerializer(data=data)

            else:
                data['password'] = data['textPassword']
                serializer1 = UserSerializer(data=data)
            if serializer1.is_valid():
                data['business_name']=request.data.get('business_name')
                if data['business_name'] is None or data['business_name'] =='':
                    data['business_name']=str(request.data.get('business_name')).lower()
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide business name", "status":"error"}})
                
                # data['parent_service']=request.data.get('parent_service')
                # if data['parent_service'] is None or data['parent_service'] =='':
                #     return Response({ "data":{},"response":{"n":0,"msg":"Please select parent service", "status":"error"}})
                
                # data['child_service']=request.data.get('child_service')
                # if data['child_service'] is None or data['child_service'] =='':
                #     return Response({ "data":{},"response":{"n":0,"msg":"Please select child service", "status":"error"}})
                
                # data['mobile_number']= request.data.get('mobileNumber')
                # data['alternate_mobile_number'] = request.data.get('alternate_mobile_number')
                # data['description'] = request.data.get('description')
                # data['website'] = request.data.get('website')
                # data['lattitude'] = request.data.get('lattitude')
                # data['longitude'] = request.data.get('longitude')
                # data['radius'] = request.data.get('radius')

                # business_logo = request.FILES.get('business_logo')
                # if business_logo is not None and business_logo !='':
                #     data['business_logo']=business_logo
                
            
                business_name_obj = ServiceProvider.objects.filter(isActive=True, business_name=data['business_name'].lower()).first()        
                if business_name_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business name already exist", "status": "error"}})        
                else:

                    already_exist_service_provider_obj = ServiceProvider.objects.filter(isActive=True, userid=logined_user_id).first()        
                    if already_exist_service_provider_obj is not None:
                        return Response({"data":'',"response": {"n": 0, "msg": "This user is already register as service provider", "status": "error"}})     
                    
                    serializer1.save()
                    userid = serializer1.data['id']
                    data['userid'] = str(userid)
                    
                    serializer2 = ServiceProviderSerializer(data=data)
                    if serializer2.is_valid():
                        serializer2.save()
                        free_subscription = mark_1_month_free_subscription(serializer1.data['id'])
                        if free_subscription:
                            return Response({"data": serializer2.data, "response": {"n": 1, "msg": "Thank you for joining Mozil!\nYour registration is complete and your free plan has been activated for 30 days. Start exploring all the features available to you.", "status": "success"}})

                        return Response({"data":serializer2.data,"response": {"n": 1, "msg": "Service  Provider details registered successfully","status":"success"}})
                    else:
                        first_key, first_value = next(iter(serializer2.errors.items()))
                        return Response({"data" : serializer2.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
            
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
    



class register_consumer_as_service_provider(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        # if request_data['Username'] is None or request_data['Username'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide owner name", "status":"error"}})
        # data['Username']=request.data.get('Username')

        # data['email']=str(request.data.get('email')).lower()
        # if data['email'] is None or data['email'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})
        
        # data['textPassword']=request.data.get('textPassword')
        # if data['textPassword'] is None or data['textPassword'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        # data['mobileNumber']=request.data.get('mobileNumber')
        # if data['mobileNumber'] is None or data['mobileNumber'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})

        # data['password'] = data['textPassword']
        data['role'] = 2
        update_user_obj = User.objects.filter(isActive=True, id=str(request.user.id)).first()
        if update_user_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "user not found", "status": "error"}})        
        else:
            serializer1 = UserSerializer(update_user_obj,data=data,partial=True)
            if serializer1.is_valid():
                data['business_name']=request.data.get('business_name')
                if data['business_name'] is None or data['business_name'] =='':
                    data['business_name']=str(request.data.get('business_name')).lower()
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide business name", "status":"error"}})
                  
            
                business_name_obj = ServiceProvider.objects.filter(isActive=True, business_name=data['business_name'].lower()).first()        
                if business_name_obj is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Business name already exist", "status": "error"}})        
                else:
                    already_exists_service_provider=ServiceProvider.objects.filter(isActive=True, userid=str(request.user.id)).first()  
                    if already_exists_service_provider is not None:
                        return Response({"data":'',"response": {"n": 0, "msg": "This user already exists as service provider", "status": "error"}})        

                    serializer1.save()
                    userid = serializer1.data['id']
                    data['userid'] = str(userid)


                    serializer2 = ServiceProviderSerializer(data=data)
                    if serializer2.is_valid():
                        serializer2.save()
                        free_subscription = mark_1_month_free_subscription(serializer1.data['id'])
                        if free_subscription:
                            return Response({"data": serializer2.data, "response": {"n": 1, "msg": "Thank you for joining Mozil!\nYour registration is complete and your free plan has been activated for 30 days. Start exploring all the features available to you.", "status": "success"}})

                        return Response({"data":serializer2.data,"response": {"n": 1, "msg": "Service  Provider details registered successfully","status":"success"}})
                    else:
                        first_key, first_value = next(iter(serializer2.errors.items()))
                        return Response({"data" : serializer2.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
            
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
    


























class register_new_consumer(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide consumer name", "status":"error"}})
        data['email']=str(request.data.get('email')).lower()
        if data['email'] is None or data['email'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide email id", "status":"error"}})
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        # data['mobileNumber']=request.data.get('mobileNumber')
        # if data['mobileNumber'] is None or data['mobileNumber'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})

        data['password'] = data['textPassword']
        data['isActive'] = True
        data['role'] = 3

        
        role_objs = Role.objects.filter(isActive=True,id=3).first()
        if role_objs is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not exist", "status": "error"}})        

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        else:
            serializer1 = UserSerializer(data=data)
            if serializer1.is_valid():
                serializer1.save()
                return Response({"data":serializer1.data,"response": {"n": 1, "msg": "Registration successfull", "status": "error"}})        
            else:
                first_key, first_value = next(iter(serializer1.errors.items()))
                return Response({"data" : serializer1.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
    



















class service_provider_offered_service_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        service_provider_objs = ServiceProviderOfferedServices.objects.filter(service_provider_id=service_provider_id,isActive=True).order_by('id')
        page4 = self.paginate_queryset(service_provider_objs)
        serializer = ServiceProviderOfferedServicesSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)


class service_provider_offered_service(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        service_provider_objs = ServiceProviderOfferedServices.objects.filter(service_provider_id=service_provider_id,isActive=True).order_by('id')
        page4 = self.paginate_queryset(service_provider_objs)
        serializer = ServiceProviderOfferedServicesSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)


class add_service_provider_offered_service(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()

        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":{},"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid
        data['short_description']=request.data.get('short_description')
        if data['short_description'] is None or data['short_description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide short description", "status":"error"}})
        
        data['long_description']=request.data.get('long_description')
        if data['long_description'] is None or data['long_description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide long description", "status":"error"}})
        
        data['rate']=request.data.get('rate')
        if data['rate'] is None or data['rate'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service rate", "status":"error"}})

        data['isActive'] = True

        offered_service_obj = ServiceProviderOfferedServices.objects.filter(isActive=True,service_provider_id=data['service_provider_id'], short_description=data['short_description']).first()        
        if offered_service_obj is not None:
            return Response({"data":{},"response": {"n": 0, "msg": "Offered Service already exist try another service", "status": "error"}})  
      

        serializer = ServiceProviderOfferedServicesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Offered service added successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class update_service_provider_offered_service(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['offered_service_id']=request.data.get('offered_service_id')
        if data['offered_service_id'] is None or data['offered_service_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide offered service id", "status":"error"}})
        
        update_obj = ServiceProviderOfferedServices.objects.filter(isActive=True, id=data['offered_service_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Offered service  not found", "status": "error"}})
        
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid

        data['short_description']=request.data.get('short_description')
        if data['short_description'] is None or data['short_description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide short description", "status":"error"}})
        
        data['long_description']=request.data.get('long_description')
        if data['long_description'] is None or data['long_description'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide long description", "status":"error"}})
        
        data['rate']=request.data.get('rate')
        if data['rate'] is None or data['rate'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service rate", "status":"error"}})

        data['isActive'] = True

        offered_service_obj = ServiceProviderOfferedServices.objects.filter(isActive=True,service_provider_id=data['service_provider_id'], short_description=data['short_description']).exclude(id=update_obj.id).first()        
        if offered_service_obj is not None:
            return Response({"data":{},"response": {"n": 0, "msg": "Offered Service already exist try another service", "status": "error"}})  
      

        serializer = ServiceProviderOfferedServicesSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Offered service updated successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class delete_service_provider_offered_service(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['offered_service_id']=request.data.get('offered_service_id')
        if data['offered_service_id'] is None or data['offered_service_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide offered service id", "status":"error"}})
        
        update_obj = ServiceProviderOfferedServices.objects.filter(isActive=True, id=data['offered_service_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Offered service  not found", "status": "error"}})
        

        data['isActive'] = False


      

        serializer = ServiceProviderOfferedServicesSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Offered service deleted successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class get_service_provider_offered_service_by_id(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['offered_service_id']=request.data.get('offered_service_id')
        if data['offered_service_id'] is None or data['offered_service_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide offered service id", "status":"error"}})
        
        update_obj = ServiceProviderOfferedServices.objects.filter(isActive=True, id=data['offered_service_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Offered service  not found", "status": "error"}})
        



      

        serializer = ServiceProviderOfferedServicesSerializer(update_obj)
        

        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Offered service found successfully","status":"success"}})

class get_service_provider_highlights(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        if service_provider_id is not None:
            highlights_obj= ServiceProviderHighlights.objects.filter(isActive=True,service_provider_id=service_provider_id).order_by('id')
            serializer = ServiceProviderHighlightsSerializer(highlights_obj ,many=True)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Highlights list found successfully","status": "success"}})
        else:
            return Response({"data":[],"response": {"n": 0, "msg": "Please provide service provider id","status": "error"}})

class add_service_provider_highlight(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid
        data['name']=request.data.get('name')
        if data['name'] is None or data['name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide name", "status":"error"}})
        
        data['description']=request.data.get('description')
        # if data['description'] is None or data['description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide long description", "status":"error"}})
        

        data['isActive'] = True

        sticker = request.FILES.get('sticker')
        if sticker is not None and sticker !='':
            data['sticker']=sticker
      

        serializer = ServiceProviderHighlightsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Highlight added successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class delete_service_provider_highlight(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['highlight_id']=request.data.get('highlight_id')
        if data['highlight_id'] is None or data['highlight_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide highlight id", "status":"error"}})
        
        update_obj = ServiceProviderHighlights.objects.filter(isActive=True, id=data['highlight_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Highlight  not found", "status": "error"}})
        

        data['isActive'] = False


      

        serializer = ServiceProviderHighlightsSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Highlight deleted successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class get_service_provider_highlight_by_id(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['highlight_id']=request.data.get('highlight_id')
        if data['highlight_id'] is None or data['highlight_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide highlight id", "status":"error"}})
        
        update_obj = ServiceProviderHighlights.objects.filter(isActive=True, id=data['highlight_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Highlight  not found", "status": "error"}})
        



        serializer = ServiceProviderHighlightsSerializer(update_obj)
   

        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Highlight found successfully","status":"success"}})



class edit_service_provider_highlight(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        # request_data = request.data.copy()

        data['highlight_id']=request.data.get('highlight_id')
        if data['highlight_id'] is None or data['highlight_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide highlight id", "status":"error"}})
        
        update_obj = ServiceProviderHighlights.objects.filter(isActive=True, id=data['highlight_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Highlight  not found", "status": "error"}})
        




        

        data['name']=request.data.get('name')
        if data['name'] is None or data['name'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide name", "status":"error"}})
        
        data['description']=request.data.get('description')
        # if data['description'] is None or data['description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide long description", "status":"error"}})
        

        data['isActive'] = True

        sticker = request.FILES.get('sticker')
        if sticker is not None and sticker !='':
            data['sticker']=sticker
      

        serializer = ServiceProviderHighlightsSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Highlight updated successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  


class add_service_provider_portfolio(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})

        service_providerobj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if service_providerobj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})  
        

        data['userid']=service_providerobj.userid
        data['heading']=request.data.get('heading')
        if data['heading'] is None or data['heading'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service heading", "status":"error"}})


        data['short_description']=request.data.get('short_description')
        # if data['short_description'] is None or data['short_description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide short description", "status":"error"}})
        
        data['long_description']=request.data.get('long_description')
        # if data['long_description'] is None or data['long_description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide long description", "status":"error"}})
        

        data['isActive'] = True

      

        serializer = ServiceProviderPortfolioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            media_list=request.FILES.getlist('media[]')
            for media in media_list:
                d1={
                    "userid":data['userid'],
                    "service_provider_id":data['service_provider_id'],
                    "portfolio_id":serializer.data['id'],
                    "media":media,
                }
                serializer1=ServiceProviderPortfolioMediaSerializer(data=d1)
                if serializer1.is_valid():
                    serializer1.save()

                else:
                    print("serializer1",serializer1.errors)

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio added successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class get_service_provider_portfolio(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        if service_provider_id is not None:
            portfolio_obj= ServiceProviderPortfolio.objects.filter(isActive=True,service_provider_id=service_provider_id).order_by('id')
            serializer = CustomServiceProviderPortfolioSerializer(portfolio_obj ,many=True)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio list found successfully","status": "success"}})
        else:
            return Response({"data":[],"response": {"n": 0, "msg": "Please provide service provider id","status": "error"}})

class delete_service_provider_portfolio(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['portfolio_id']=request.data.get('portfolio_id')
        if data['portfolio_id'] is None or data['portfolio_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide portfolio id", "status":"error"}})
        
        update_obj = ServiceProviderPortfolio.objects.filter(isActive=True, id=data['portfolio_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Portfolio  not found", "status": "error"}})
        

        data['isActive'] = False

        serializer = ServiceProviderPortfolioSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            delete_media=ServiceProviderPortfolioMedia.objects.filter(portfolio_id=serializer.data['id']).update(isActive=False)

            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio deleted successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class delete_portfolio_media(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['media_id']=request.data.get('media_id')
        if data['media_id'] is None or data['media_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide media id", "status":"error"}})
        

        update_obj = ServiceProviderPortfolioMedia.objects.filter(isActive=True, id=data['media_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Media id  not found", "status": "error"}})
        
        data['isActive'] = False
        serializer = ServiceProviderPortfolioMediaSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio media deleted successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class update_service_provider_portfolio(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        # request_data = request.data.copy()

        data['portfolio_id']=request.data.get('portfolio_id')
        if data['portfolio_id'] is None or data['portfolio_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide portfolio id", "status":"error"}})
        
        update_obj = ServiceProviderPortfolio.objects.filter(isActive=True, id=data['portfolio_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Portfolio  not found", "status": "error"}})
        




        

        data['heading']=request.data.get('heading')
        if data['heading'] is None or data['heading'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide heading", "status":"error"}})
        
        data['short_description']=request.data.get('short_description')
        # if data['short_description'] is None or data['short_description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide  short description", "status":"error"}})
        data['long_description']=request.data.get('long_description')
        # if data['long_description'] is None or data['long_description'] =='':
        #     return Response({ "data":{},"response":{"n":0,"msg":"Please provide  long description", "status":"error"}})
        

        data['isActive'] = True


      

        serializer = ServiceProviderPortfolioSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            media_list=request.FILES.getlist('media[]')
            for media in media_list:
                d1={
                    "userid":serializer.data['userid'],
                    "service_provider_id":serializer.data['service_provider_id'],
                    "portfolio_id":serializer.data['id'],
                    "media":media,
                }
                serializer1=ServiceProviderPortfolioMediaSerializer(data=d1)
                if serializer1.is_valid():
                    serializer1.save()

                else:
                    print("serializer1",serializer1.errors)


            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio updated successfully","status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class get_service_provider_portfolio_by_id(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        
        data['portfolio_id']=request.data.get('portfolio_id')
        if data['portfolio_id'] is None or data['portfolio_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide portfolio id", "status":"error"}})
        
        update_obj = ServiceProviderPortfolio.objects.filter(isActive=True, id=data['portfolio_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Portfolio  not found", "status": "error"}})
        


        serializer = ServiceProviderPortfolioSerializer(update_obj)

        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Portfolio found successfully","status":"success"}})
     
class change_verification(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})
        
        update_obj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})
        if update_obj.license_verification_status:

            data['license_verification_status'] = False
            msg="Service Provider Unverified Successfully."
        else:
            data['license_verification_status'] = True
            msg="Service Provider Verified Successfully."

        serializer =ServiceProviderSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": msg,"status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class change_guarented(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        
        data['service_provider_id']=request.data.get('service_provider_id')
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})
        
        update_obj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})
        if update_obj.mozil_guarented:

            data['mozil_guarented'] = False
            msg="Service Provider Status Changed To Non-Guarented Successfully."
        else:
            data['mozil_guarented'] = True
            msg="Service Provider Status Changed To Guarented Successfully."

        serializer =ServiceProviderSerializer(update_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"response": {"n": 1, "msg": msg,"status":"success"}})
        else:
            first_key, first_value = next(iter(serializer.errors.items()))
            return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class change_status(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        
        data['service_provider_id']=str(request.data.get('service_provider_id'))
        if data['service_provider_id'] is None or data['service_provider_id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide service provider id", "status":"error"}})
        
        update_obj = ServiceProvider.objects.filter(isActive=True, id=data['service_provider_id']).first()
        if update_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "Service provider not found", "status": "error"}})
        
        user_obj=User.objects.filter(id=str(update_obj.userid),isActive=True).first()
        if user_obj is not None:
            if user_obj.status:
                data['status'] = False
                msg="Service Provider Deactivated Successfully."
            else:
                data['status'] = True
                msg="Service Provider Activated Successfully."

            serializer =UserSerializer(user_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": msg,"status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":{},"response": {"n": 0, "msg": 'User not found ',"status":"error"}})

class change_user_status(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        
        data['id']=str(request.data.get('id'))
        if data['id'] is None or data['id'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide User id", "status":"error"}})
        
        user_obj = User.objects.filter(isActive=True, id=data['id']).first()
        if user_obj is None:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found", "status": "error"}})
        
        if user_obj is not None:
            if user_obj.status:
                data['status'] = False
                msg="User Deactivated Successfully."
            else:
                data['status'] = True
                msg="User Activated Successfully."

            serializer =UserSerializer(user_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": msg,"status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":{},"response": {"n": 0, "msg": 'User not found ',"status":"error"}})

class check_business_name_availablity(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['business_name']=request.data.get('business_name')
        if data['business_name'] is None or data['business_name'] =='':
            data['business_name']=str(request.data.get('business_name')).lower()
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide business name", "status":"error"}})

        business_name_obj = ServiceProvider.objects.filter(isActive=True, business_name=data['business_name'].lower()).first()        
        if business_name_obj is not None:
            return Response({"data":{},"response": {"n": 0, "msg": "Business name already exist try another business name", "status": "error"}})        
        else:
            return Response({"data":{},"response": {"n": 1, "msg": "Business name available","status":"success"}})

class check_email_availablity(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = {}
        email = request.data.get('email', '').strip().lower()
        logined_user_id = str(request.data.get('logined_user_id', ''))
        data['email'] = email

        # Check if email is provided
        if not email:
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Please provide email", "status": "error"}
            })

        # Validate email format using regex
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Please provide valid email format", "status": "error"}
            })

        # Check if email already exists

        print("logined_user_id",logined_user_id)
        email_obj = User.objects.filter(isActive=True, email=email)
        if logined_user_id is not None and logined_user_id !='':
            email_obj=email_obj.exclude(id=logined_user_id).first()
        else:
            email_obj=email_obj.first()





        if email_obj:
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Email already exists, try another email", "status": "error"}
            })
        else:
            return Response({
                "data": {}, 
                "response": {"n": 1, "msg": "Email available", "status": "success"}
            })

class send_verification_otp_mail(GenericAPIView):

    def post(self, request):
        email = request.data.get("email", "").strip().lower()

        # Validate email
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not email or not re.match(email_regex, email):
            return Response({
                "data": {}, 
                "response": {"n": 0, "msg": "Invalid or missing email", "status": "error"}
            },)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save to DB (overwrite if email already exists)
        EmailOTPVerification.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp,
                'created_at': timezone.now()
            }
        )
        html_content = render_to_string('Mails/otp_email_template.html', {'otp': otp})
        msg = EmailMultiAlternatives(
            subject="Your OTP Verification Code",
            body=f"Your OTP code is {otp}. It will expire in 10 minutes.",
            from_email="no-reply@zentrotechnologies.com",
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send(fail_silently=False)
            print("Email sent to", email)
        except Exception as e:
            print("EMAIL SEND ERROR:", e)



        return Response({
            "data": {"email": email}, 
            "response": {"n": 1, "msg": "OTP sent successfully", "status": "success"}
        })

class ValidateOTP(GenericAPIView):
    def post(self, request):
        # Get email and OTP from request data
        email = request.data.get("email", "").strip().lower()
        otp = request.data.get("otp", "").strip()

        # Validate email
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not email or not re.match(email_regex, email):
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid or missing email", "status": "error"}
            })

        # Validate OTP
        if not otp:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "OTP is required", "status": "error"}
            })

        # Fetch the OTP record from the database
        otp_record = EmailOTPVerification.objects.filter(email=email).first()

        if not otp_record:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "No OTP record found for this email", "status": "error"}
            })

        # Check if OTP is expired (Optional: Add expiration time like 10 minutes)
        otp_expiry_time = otp_record.created_at + timedelta(minutes=10)
        print("otp_expiry_time",timezone.now(),otp_expiry_time)
        if timezone.now() > otp_expiry_time:

        # if make_aware(datetime.now()) > otp_expiry_time:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "OTP has expired, please request a new one", "status": "error"}
            })

        # Compare provided OTP with the stored OTP
        if otp == otp_record.otp:
            return Response({
                "data": {},
                "response": {"n": 1, "msg": "OTP validated successfully", "status": "success"}
            })
        else:
            return Response({
                "data": {},
                "response": {"n": 0, "msg": "Invalid OTP", "status": "error"}
            })

class service_provider_filter_pagination_api(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    
    def post(self, request):
        service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('id')
        
        # Get filter parameters from request
        lattitude = request.data.get('lattitude')
        longitude = request.data.get('longitude')
        parent_service = request.data.get('parent_service')
        child_service = request.data.get('child_service')
        license_verification_status = request.data.get('license_verification_status')
        mozil_guarented = request.data.get('mozil_guarented')
        average_rating = request.data.get('average_rating')
        
        # Apply basic filters
        if parent_service:
            service_provider_objs = service_provider_objs.filter(parent_service=parent_service)
        if child_service:
            service_provider_objs = service_provider_objs.filter(child_service=child_service)
        if license_verification_status:
            service_provider_objs = service_provider_objs.filter(license_verification_status=license_verification_status)
        if mozil_guarented:
            service_provider_objs = service_provider_objs.filter(mozil_guarented=mozil_guarented)
        if average_rating:
            service_provider_objs = service_provider_objs.filter(average_rating__gte=average_rating)
        
        # Apply distance filter if coordinates are provided
        if lattitude and longitude:
            try:
                lat = float(lattitude)
                lng = float(longitude)
                
                # Earth radius in kilometers
                earth_radius = 6371
                
                # Convert latitude and longitude from degrees to radians
                lat_rad = Radians(F('lattitude'))
                lng_rad = Radians(F('longitude'))
                user_lat_rad = math.radians(lat)
                user_lng_rad = math.radians(lng)
                
                # Haversine formula to calculate distance
                dlat = user_lat_rad - lat_rad
                dlng = user_lng_rad - lng_rad
                
                a = (Power(Sin(dlat / 2), 2) + 
                     Cos(lat_rad) * Cos(user_lat_rad) * 
                     Power(Sin(dlng / 2), 2))
                
                c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
                distance = earth_radius * c
                
                # Filter for service providers within 1km
                service_provider_objs = service_provider_objs.annotate(
                    distance=ExpressionWrapper(distance, output_field=FloatField())
                ).filter(distance__lte=1)
                
            except (ValueError, TypeError):
                # Handle invalid coordinate values
                pass
        
        # Paginate and return results
        page = self.paginate_queryset(service_provider_objs)
        serializer = CustomServiceProviderSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class service_provider_filter(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('id')
        
        # Get filter parameters from request
        lattitude = request.data.get('lattitude')
        longitude = request.data.get('longitude')
        parent_service = request.data.get('parent_service')
        child_service = request.data.get('child_service')
        license_verification_status = request.data.get('license_verification_status')
        mozil_guarented = request.data.get('mozil_guarented')
        average_rating = request.data.get('average_rating')
        
        # Apply basic filters
        if parent_service:
            service_provider_objs = service_provider_objs.filter(parent_service=parent_service)
        if child_service:
            service_provider_objs = service_provider_objs.filter(child_service=child_service)
        if license_verification_status:
            service_provider_objs = service_provider_objs.filter(license_verification_status=license_verification_status)
        if mozil_guarented:
            service_provider_objs = service_provider_objs.filter(mozil_guarented=mozil_guarented)
        if average_rating:
            service_provider_objs = service_provider_objs.filter(average_rating__gte=average_rating)
        
        # Apply distance filter if coordinates are provided
        if lattitude and longitude:
            try:
                lat = float(lattitude)
                lng = float(longitude)
                
                # Earth radius in kilometers
                earth_radius = 6371
                
                # Convert latitude and longitude from degrees to radians
                lat_rad = Radians(F('lattitude'))
                lng_rad = Radians(F('longitude'))
                user_lat_rad = math.radians(lat)
                user_lng_rad = math.radians(lng)
                
                # Haversine formula to calculate distance
                dlat = user_lat_rad - lat_rad
                dlng = user_lng_rad - lng_rad
                
                a = (Power(Sin(dlat / 2), 2) + 
                     Cos(lat_rad) * Cos(user_lat_rad) * 
                     Power(Sin(dlng / 2), 2))
                
                c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
                distance = earth_radius * c
                
                # Filter for service providers within 1km
                service_provider_objs = service_provider_objs.annotate(
                    distance=ExpressionWrapper(distance, output_field=FloatField())
                ).filter(distance__lte=1)
                
            except (ValueError, TypeError):
                # Handle invalid coordinate values
                pass
        
        # Paginate and return results
        print("service_provider_objs",service_provider_objs.count())
        if service_provider_objs.exists():
            serializer1 = CustomServiceProviderSerializer(service_provider_objs, many=True)
            return Response({
                    "data": serializer1.data,
                    "response": {"n": 1, "msg": "Service providers found successfully", "status": "success"}
                })
        else:
            return Response({
                    "data": [],
                    "response": {"n": 0, "msg": "Service providers not found", "status": "error"}
                })
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Cast  # Add this import

class service_finder(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('id')
        
        # Get filter parameters from request
        lattitude = request.data.get('lattitude')
        longitude = request.data.get('longitude')
        parent_service = request.data.get('parent_service')
        child_service = request.data.get('child_service')
        license_verification_status = request.data.get('license_verification_status')
        mozil_guarented = request.data.get('mozil_guarented')
        average_rating = request.data.get('average_rating')
        search = request.data.get('search')
        region = request.data.get('region')
        range_meter = request.data.get('range_meter', 15000)  # Default 1km if not provided

        # Search functionality
        if search is not None and search != '':
            parent_service_ids = list(ParentServices.objects.filter(Name__icontains=search, isActive=True).values_list('id', flat=True))
            child_service_ids = list(ChildServices.objects.filter(Name__icontains=search, isActive=True).values_list('id', flat=True))
            service_provider_ids1 = list(ServiceProvider.objects.filter(business_name__icontains=search, isActive=True).values_list('id', flat=True))
            service_provider_ids2 = list(ServiceProviderOfferedServices.objects.filter(short_description__icontains=search, isActive=True).values_list('service_provider_id', flat=True))
            service_provider_ids3 = list(ServiceProviderHighlights.objects.filter(name__icontains=search, isActive=True).values_list('service_provider_id', flat=True))
            service_provider_ids = service_provider_ids1 + service_provider_ids2 + service_provider_ids3
            
            if parent_service_ids:
                service_provider_objs = service_provider_objs.filter(parent_service__in=parent_service_ids)
            if child_service_ids:
                service_provider_objs = service_provider_objs.filter(child_service__in=child_service_ids)
            if service_provider_ids:
                service_provider_objs = service_provider_objs.filter(id__in=service_provider_ids)

        childservice_objs = ChildServices.objects.filter(isActive=True).order_by('id')

        # Apply basic filters
        if parent_service:
            service_provider_objs = service_provider_objs.filter(parent_service=parent_service)
            childservice_objs=childservice_objs.filter(ParentServiceId=parent_service)
            ServiceSearchLog.objects.create(
                ParentServiceId=parent_service,
                search_text=search if search is not None else '',
            )





        if child_service:
            service_provider_objs = service_provider_objs.filter(child_service=child_service)
            ServiceSearchLog.objects.create(
                ChildServiceId=child_service,
                search_text=search if search is not None else '',
            )
        if license_verification_status:
            service_provider_objs = service_provider_objs.filter(license_verification_status=license_verification_status)
        if mozil_guarented:
            service_provider_objs = service_provider_objs.filter(mozil_guarented=mozil_guarented)
        if average_rating:
            service_provider_objs = service_provider_objs.filter(average_rating__gte=average_rating)
        if region is not None and region != '':
            service_provider_objs = service_provider_objs.filter(region=region)
        
        # Apply distance filter if coordinates are provided
        if lattitude and longitude:
            try:
                lat = float(lattitude)
                lng = float(longitude)
                range_km = float(range_meter) / 1000  # Convert meters to kilometers
                
                # Filter out records with invalid coordinates
                valid_providers = service_provider_objs
    
                
                # Only proceed if we have providers with valid coordinates
                if valid_providers.exists():
                    # Earth radius in kilometers
                    earth_radius = 6371
                
                    # Calculate distance for valid providers
                    service_provider_objs = valid_providers.annotate(
                        distance=ExpressionWrapper(
                            earth_radius * 2 * ATan2(
                                Sqrt(
                                    Power(Sin((Radians(lat) - Radians(Cast(F('lattitude'), FloatField()))) / 2), 2) +
                                    Cos(Radians(Cast(F('lattitude'), FloatField()))) * 
                                    Cos(Radians(lat)) * 
                                    Power(Sin((Radians(lng) - Radians(Cast(F('longitude'), FloatField()))) / 2), 2)
                                ),
                                Sqrt(1 - (
                                    Power(Sin((Radians(lat) - Radians(Cast(F('lattitude'), FloatField()))) / 2), 2) +
                                    Cos(Radians(Cast(F('lattitude'), FloatField()))) * 
                                    Cos(Radians(lat)) * 
                                    Power(Sin((Radians(lng) - Radians(Cast(F('longitude'), FloatField()))) / 2), 2)
                                )
                                )
                            ),
                            output_field=FloatField()
                        )
                    ).filter(distance__lte=range_km).order_by('distance')
                
            except (ValueError, TypeError) as e:
                print(f"Error calculating distance: {e}")


        child_services_serializer = ChildServicesSerializer(childservice_objs, many=True)

        if service_provider_objs.exists():
            serializer1 = CustomServiceProviderSerializer(service_provider_objs, many=True)
            return Response({
                "data": {'service_providers': serializer1.data, 'child_services': child_services_serializer.data},
                "response": {"n": 1, "msg": "service providers found successfully", "status": "success"}
            })
        else:
            return Response({
                "data": {'service_providers': [], 'child_services': child_services_serializer.data},
                "response": {"n": 0, "msg": "service providers not found", "status": "error"}
            })


class top_rated_service_providers(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        service_provider_objs = ServiceProvider.objects.filter(isActive=True).exclude(average_rating__isnull=True).order_by('-average_rating')
        # Get filter parameters from request
        # Get filter parameters from request
        lattitude = request.data.get('lattitude')
        longitude = request.data.get('longitude')
        parent_service = request.data.get('parent_service')
        child_service = request.data.get('child_service')
        license_verification_status = request.data.get('license_verification_status')
        mozil_guarented = request.data.get('mozil_guarented')
        average_rating = request.data.get('average_rating')
        search = request.data.get('search')
        region = request.data.get('region')
        range_meter = request.data.get('range_meter', 15000)  # Default 1km if not provided

        # Search functionality
        if search is not None and search != '':
            parent_service_ids = list(ParentServices.objects.filter(Name__icontains=search, isActive=True).values_list('id', flat=True))
            child_service_ids = list(ChildServices.objects.filter(Name__icontains=search, isActive=True).values_list('id', flat=True))
            service_provider_ids1 = list(ServiceProvider.objects.filter(business_name__icontains=search, isActive=True).values_list('id', flat=True))
            service_provider_ids2 = list(ServiceProviderOfferedServices.objects.filter(short_description__icontains=search, isActive=True).values_list('service_provider_id', flat=True))
            service_provider_ids3 = list(ServiceProviderHighlights.objects.filter(name__icontains=search, isActive=True).values_list('service_provider_id', flat=True))
            service_provider_ids = service_provider_ids1 + service_provider_ids2 + service_provider_ids3
            
            if parent_service_ids:
                service_provider_objs = service_provider_objs.filter(parent_service__in=parent_service_ids)
            if child_service_ids:
                service_provider_objs = service_provider_objs.filter(child_service__in=child_service_ids)
            if service_provider_ids:
                service_provider_objs = service_provider_objs.filter(id__in=service_provider_ids)

        childservice_objs = ChildServices.objects.filter(isActive=True).order_by('id')

        # Apply basic filters
        if parent_service:
            service_provider_objs = service_provider_objs.filter(parent_service=parent_service)
            childservice_objs = childservice_objs.filter(ParentServiceId=parent_service)
        if child_service:
            service_provider_objs = service_provider_objs.filter(child_service=child_service)
        if license_verification_status:
            service_provider_objs = service_provider_objs.filter(license_verification_status=license_verification_status)
        if mozil_guarented:
            service_provider_objs = service_provider_objs.filter(mozil_guarented=mozil_guarented)
        if average_rating:
            service_provider_objs = service_provider_objs.filter(average_rating__gte=average_rating)
        if region is not None and region != '':
            service_provider_objs = service_provider_objs.filter(region=region)
        
        # Apply distance filter if coordinates are provided
        if lattitude and longitude:
            try:
                lat = float(lattitude)
                lng = float(longitude)
                range_km = float(range_meter) / 1000  # Convert meters to kilometers
                
                # Filter out records with invalid coordinates
                valid_providers = service_provider_objs
    
                
                # Only proceed if we have providers with valid coordinates
                if valid_providers.exists():
                    # Earth radius in kilometers
                    earth_radius = 6371
                
                    # Calculate distance for valid providers
                    service_provider_objs = valid_providers.annotate(
                        distance=ExpressionWrapper(
                            earth_radius * 2 * ATan2(
                                Sqrt(
                                    Power(Sin((Radians(lat) - Radians(Cast(F('lattitude'), FloatField()))) / 2), 2) +
                                    Cos(Radians(Cast(F('lattitude'), FloatField()))) * 
                                    Cos(Radians(lat)) * 
                                    Power(Sin((Radians(lng) - Radians(Cast(F('longitude'), FloatField()))) / 2), 2)
                                ),
                                Sqrt(1 - (
                                    Power(Sin((Radians(lat) - Radians(Cast(F('lattitude'), FloatField()))) / 2), 2) +
                                    Cos(Radians(Cast(F('lattitude'), FloatField()))) * 
                                    Cos(Radians(lat)) * 
                                    Power(Sin((Radians(lng) - Radians(Cast(F('longitude'), FloatField()))) / 2), 2)
                                )
                                )
                            ),
                            output_field=FloatField()
                        )
                    ).filter(distance__lte=range_km).order_by('distance')
                
            except (ValueError, TypeError) as e:
                print(f"Error calculating distance: {e}")
        
        # Paginate and return results
        # print("service_provider_objs",service_provider_objs.count())
        child_services_serializer = ChildServicesSerializer(childservice_objs,many=True)

        if service_provider_objs.exists():
            serializer1 = CustomServiceProviderSerializer(service_provider_objs, many=True)
            return Response({
                    "data": {'service_providers':serializer1.data,'child_services':child_services_serializer.data},
                    "response": {"n": 1, "msg": "service providers found successfully", "status": "success"}
                })
        else:
            return Response({
                    "data": {'service_providers':[],'child_services':child_services_serializer.data},
                    "response": {"n": 0, "msg": "service providers not found", "status": "error"}
                })

class view_service_provider_all_details(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        
        # Get filter parameters from request

        service_provider_id=request.data.get('service_provider_id')
        if service_provider_id is not None and service_provider_id !='':
            service_provider_obj = ServiceProvider.objects.filter(id=service_provider_id,isActive=True).first()
            if service_provider_obj is not None:
                serializer1 = CustomServiceProviderSerializer(service_provider_obj)
                return Response({
                        "data": serializer1.data,
                        "response": {"n": 1, "msg": "service provider found successfully", "status": "success"}
                    })
            else:
                return Response({
                        "data":{},
                        "response": {"n": 0, "msg": "service providers not found", "status": "error"}
                    })
        else:
            return Response({
                    "data":{},
                    "response": {"n": 0, "msg": "service providers id not found", "status": "error"}
                })

# class parent_service_suggestive_search(GenericAPIView):
#     # authentication_classes = [userJWTAuthentication]
#     # permission_classes = (permissions.IsAuthenticated,)
    
#     def post(self, request):

#         service_provider_objs = ServiceProvider.objects.filter(isActive=True).order_by('id')
#         # Get filter parameters from request
#         search=request.data.get('search')
#         if search is not None and search !='':

#             service_provider_ids1=list(ServiceProvider.objects.filter(business_name__icontains=search,isActive=True).values_list('id',flat=True))
#             service_provider_ids2=list(ServiceProviderOfferedServices.objects.filter(short_description__icontains=search,isActive=True).values_list('service_provider_id',flat=True))
#             service_provider_ids3=list(ServiceProviderHighlights.objects.filter(name__icontains=search,isActive=True).values_list('service_provider_id',flat=True))
#             service_provider_ids=service_provider_ids1+service_provider_ids2+service_provider_ids3
            
#             print("service_provider_ids",service_provider_ids)




#             parent_service_ids=list(ParentServices.objects.filter(Name__icontains=search,isActive=True).values_list('id',flat=True))
#             child_service_ids=list(ChildServices.objects.filter(Name__icontains=search,isActive=True).values_list('id',flat=True))
            
#             if parent_service_ids !=[]:
#                 service_provider_objs=service_provider_objs.filter(parent_service__in=parent_service_ids)

#             if child_service_ids !=[]:
#                 service_provider_objs=service_provider_objs.filter(child_service__in=child_service_ids)

 
#             if service_provider_ids !=[]:
#                 service_provider_objs=service_provider_objs.filter(id__in=service_provider_ids)


        

#         existing_parent_service_ids=list(service_provider_objs.values_list('parent_service',flat=True))
#         parent_services_objs=ParentServices.objects.filter(id__in=existing_parent_service_ids,isActive=True)
#         if parent_services_objs.exists():
#             parent_service_serializer=ParentServicesSerializer(parent_services_objs,many=True)

#             parent_service_serializer_list=parent_service_serializer.data
#             for parent_service in parent_service_serializer_list:
#                 parent_service_provider_objs=service_provider_objs.filter(parent_service=parent_service['id'],isActive=True)
#                 parent_service_provider_serializer=CustomServiceProviderSerializer(parent_service_provider_objs,many=True)
#                 parent_service['service_providers_list']=parent_service_provider_serializer.data
                
#                 # print("par",parent_service)



#             return Response({
#                     "data": parent_service_serializer_list,
#                     "response": {"n": 1, "msg": "service providers found successfully", "status": "success"}
#                 })
#         else:
#             return Response({
#                     "data": [],
#                     "response": {"n": 0, "msg": "service providers not found", "status": "error"}
#                 })



class parent_service_suggestive_search(GenericAPIView):
    # authentication_classes = [userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        search = request.data.get('search', '').strip()
        
        if not search:
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "Please provide a search term", "status": "error"}
            })

        # Start with all active service providers
        service_provider_objs = ServiceProvider.objects.filter(isActive=True)
        # print("0",service_provider_objs.count())
        
        # Get distinct service provider IDs that match any of our criteria
        service_provider_ids = set()

        # Search in business name
        service_provider_ids.update(
            ServiceProvider.objects.filter(
                business_name__icontains=search,
                isActive=True
            ).values_list('id', flat=True)
        )
        # print("1",service_provider_ids)

        # Search in offered services
        service_provider_ids.update(
            ServiceProviderOfferedServices.objects.filter(
                short_description__icontains=search,
                isActive=True
            ).values_list('service_provider_id', flat=True)
        )
        # print("2",service_provider_ids)


        # Search in highlights
        service_provider_ids.update(
            ServiceProviderHighlights.objects.filter(
                name__icontains=search,
                isActive=True
            ).values_list('service_provider_id', flat=True)
        )
        # print("3",service_provider_ids)

        # Search in parent services (convert IDs to strings for CharField comparison)
        parent_service_ids = ParentServices.objects.filter(
            Name__icontains=search,
            isActive=True
        ).values_list('id', flat=True)
        # print("4",service_provider_ids)
        
        service_provider_ids.update(
            ServiceProvider.objects.filter(
                parent_service__in=[str(pid) for pid in parent_service_ids],
                isActive=True
            ).values_list('id', flat=True)
        )
        # print("5",service_provider_ids)

        # Search in child services (convert IDs to strings for CharField comparison)
        child_service_ids = ChildServices.objects.filter(
            Name__icontains=search,
            isActive=True
        ).values_list('id', flat=True)
        # print("6",service_provider_ids)
        
        service_provider_ids.update(
            ServiceProvider.objects.filter(
                child_service__in=[str(cid) for cid in child_service_ids],
                isActive=True
            ).values_list('id', flat=True)
        )
        # print("7",service_provider_ids)

        # Get all matching service providers
        service_provider_objs = ServiceProvider.objects.filter(
            id__in=service_provider_ids,
            isActive=True
        ).distinct()
        # print("8",service_provider_ids)

        # Get all unique parent services from the matching providers
        parent_service_ids = service_provider_objs.values_list(
            'parent_service',
            flat=True
        ).distinct()
        # print("9",service_provider_ids)

        # Convert string IDs back to integers for ParentServices query
        parent_services_objs = ParentServices.objects.filter(
            id__in=[int(pid) for pid in parent_service_ids if pid and pid.isdigit()],
            isActive=True
        )
        # print("10",service_provider_ids)


        if not parent_services_objs.exists():
            return Response({
                "data": [],
                "response": {"n": 0, "msg": "No service providers found", "status": "error"}
            })

        # Serialize the response
        parent_service_serializer = ParentServicesSerializer(parent_services_objs, many=True)
        parent_service_data = parent_service_serializer.data

        # Add service providers to each parent service
        for parent_service in parent_service_data:
            providers = service_provider_objs.filter(
                parent_service=str(parent_service['id'])
            )
            provider_serializer = CustomServiceProviderSerializer(providers, many=True)
            parent_service['service_providers_list'] = provider_serializer.data

        return Response({
            "data": parent_service_data,
            "response": {
                "n": len(parent_service_data),
                "msg": "Service providers found successfully",
                "status": "success"
            }
        })

class get_service_provider_media_list(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        service_provider_id=request.data.get('service_provider_id')
        if service_provider_id is not None:
            portfolio_obj= ServiceProviderPortfolioMedia.objects.filter(isActive=True,service_provider_id=service_provider_id).order_by('id')
            serializer = ServiceProviderPortfolioMediaSerializer(portfolio_obj ,many=True)
            return Response({"data":serializer.data,"response": {"n": 1, "msg": "Media list found successfully","status": "success"}})
        else:
            return Response({"data":[],"response": {"n": 0, "msg": "Please provide service provider id","status": "error"}})


class delete_user_account(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = str(request.user.id)
        existemp = User.objects.filter(id=userID,isActive=True).first()
        if existemp is not None:

            data['isActive'] = False
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()

                if existemp.role_id == 1:
                    print("existemp.role_id",existemp.role_id)
                elif existemp.role_id == 2:
                    #delete service provider form service provider table
                    service_provider_obj=ServiceProvider.objects.filter(userid=userID,isActive=True).first()
                    if service_provider_obj is not None:
                        service_provider_obj.isActive=False
                        service_provider_obj.save()
                elif existemp.role_id == 3:
                    # delete customer form customer table
                    print("existemp.role_id",existemp.role_id)


                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User account deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})


