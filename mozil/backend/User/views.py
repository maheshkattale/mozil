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
from .jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from mozil.settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import make_password,check_password

from .common import CustomPagination
from django.db.models import Q


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
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[]},
                    "response":{
                    "status":"error",
                    'msg': 'Please provide email and password',
                    'n':0
                    }})
        
        userexist = User.objects.filter(email=email, isActive=True).first()
        if userexist is None:
           return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[]},
                    "response":{
                    "status":"error",
                    'msg': 'This user is not found',
                    'n':0
                    }}
                           )
        else:
            user_serializer=UserSerializer(userexist)
            p = check_password(Password,userexist.password)
            if p is False:
                return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[]},
                    "response":{
                    "status":"error",
                    'msg': 'Please enter correct password',
                    'n':0
                    }})
            else:
                useruuid = str(userexist.id)
                username = userexist.Username
                short_name = ''.join([word[0] for word in username.split()]).upper()

                role =  userexist.role_id
                Department = userexist.DepartmentId
                if Department is None or Department == '':
                    Department = ''

                Token = createtoken(useruuid,email,source)
                
                if source == "Web":
                    web_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createwebtoken = UserToken.objects.create(User=useruuid,WebToken=Token,source=source)
                elif source == "Mobile":
                    mobile_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createmobiletoken = UserToken.objects.create(User=useruuid,MobileToken=Token,source=source)
                else:
                    return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[]},
                    "response":{
                    "status":"error",
                    'msg': 'Please Provide Source',
                    'n':0
                    }
                })
                
                return Response({
                    "data" : {'token':Token,'username':username,'short_name':short_name,'user_id':useruuid,'role':role,'Department':Department},
                    "response":{
                    "n": 1 ,
                    "msg" : "login successful",
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
                        "msg" : "logout successful",
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
            userObject = User.objects.filter(id=id,isActive=True).first()
        
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
                           
                            return Response({"data":'',"response": {"n": 1, "msg": "password updated successfully","status": "success"}})
                        else:
                            return Response({"data":'',"response": {"n": 0, "msg": "password not updated ","status": "failed"}})
                    else:
                        return Response({"data":'',"response": {"n": 0, "msg": "new and confirm password not matched ","status": "failed"}})
                else:
                    return Response({"data":'',"response": {"n": 0, "msg": "old password is wrong","status": "failed"}})

        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Couldnt find id","status": "failed"}})



class forgetpasswordmail(GenericAPIView):
    def post(self,request):
        data={}
        data['Email']=request.data.get('Email')
        userdata = User.objects.filter(email=data['Email'],isActive=True,PasswordSet=True).first()
        if userdata is not None:
            email =   data['Email']
            data2 = {'user_id':userdata.id,'user_email':userdata.email,'frontend_url':frontend_url}
            html_mail = render_to_string('mails/reset_password.html',data2)
            
            mailMsg = EmailMessage(
                'Forgot Password?',
                 html_mail,
                'no-reply@onerooftech.com',
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
        empdata = User.objects.filter(id=data['id'],isActive=True).first()
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
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":"serializer is not valid","status":"failure"}})
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"user not found", "status":"failure"}})


class resetpassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['id']=request.data.get('id')
        empdata = User.objects.filter(id=data['id'],isActive=True,PasswordSet=True).first()
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
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":"serializer is not valid","status":"failure"}})
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"user not found", "status":"failure"}})
        
#role -----------------------------------------------------------------------------------------------------

class addrole(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['RoleName']=request.data.get('RoleName')
        result = []
        
        if data['RoleName'] is None or data['RoleName'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"please provide Role name", "status":"failure"}})
        
        
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
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"role added Successfully!","status":"success"}})
            else:
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":"serializer is not valid","status":"failure"}})
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"role already exist", "status":"failure"}})



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
                return Response({ "data":{},"response":{"n":0,"msg":"please provide Role name", "status":"failure"}})
        
            roleindata = Role.objects.filter(RoleName=data['RoleName'],isActive= True).exclude(id=id).first()
            if roleindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "role already exist","status": "failure"}})
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
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "role updated successfully","status": "success"}})
                else:
                    return Response({"data":serializer.errors,"response": {"n": 0, "msg": "role not updated ","status": "failure"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "role not found ","status": "failure"}})



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
                return Response({"data":serializer.errors,"response": {"n": 0, "msg": "Role not Deleted","status": "failure"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not Found","status": "failure"}})

#user----------------------------------------------------------------------------------------------------

class createuser(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"please provide user name", "status":"failure"}})
        
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"please provide user password", "status":"failure"}})
        
        data['mobileNumber']=request.data.get('mobileNumber')
        if data['mobileNumber'] is None or data['mobileNumber'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"please provide user mobile number", "status":"failure"}})
        
        data['email']=request.data.get('email')
        data['role'] = request.data.get('role')
        data['DepartmentId'] = request.data.get('DepartmentId')
        data['password'] = data['textPassword']
        data['isActive'] = True
        result = []
        if 'result' in request.data.keys():
            result = request.data.get('result')

        roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
        if roleobj is not None:
            rolename = roleobj.RoleName
            if rolename is not None and rolename != '':
                if rolename.lower() == 'gpl users':
                    data['DepartmentId'] = data['DepartmentId']
                else:
                    data['DepartmentId'] = None
            else:
                data['DepartmentId'] = None
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "Status": "Failed"}})

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=data['mobileNumber']).first()        
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "email already exist", "Status": "Failed"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "mobile already exist", "Status": "Failed"}})
        
        else:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                userid = serializer.data['id']
                for i in result:
                    print("i",i)
                    UserPermissions.objects.create(
                        userid = userid,
                        role =  data['role'],
                        add = i['create'],
                        view = i['read'],
                        edit = i['edit'],
                        delete = i['delete'],
                        menu= i['menu_id']
                    )
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "user registered successfully","status":"success"}})
            else:
                return Response({"data":serializer.errors,"response": {"n": 0, "msg": "user not registered successfully","status":"failure"}})
                
        
class userlist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        empobjects = User.objects.filter(isActive=True).order_by('id')
        serializer = CustomUserSerializer(empobjects, many=True)
        return Response({"data":serializer.data,"response": {"n": 1, "msg": "user list shown successfully","status": "success"}})



# class user_list_pagination_api(GenericAPIView):
#     authentication_classes=[userJWTAuthentication]
#     permission_classes = (permissions.IsAuthenticated,)
#     pagination_class = CustomPagination
#     def get(self,request):
#         UserMaster_objs = User.objects.filter(isActive=True).order_by('Username')
#         page4 = self.paginate_queryset(UserMaster_objs)
#         serializer = CustomUserSerializer(page4,many=True)
#         return self.get_paginated_response(serializer.data)
    

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
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "user shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "user not found  ","status": "success"}})


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
            data['DepartmentId'] = request.data.get('DepartmentId')
            data['isActive'] = True
            result = []
            if 'result' in request.data.keys():
                result = json.loads(request.data.get('result'))
            # data['updatedBy'] = str(request.user.id)

            roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
            if roleobj is not None:
                rolename = roleobj.RoleName
                if rolename is not None and rolename != '':
                    if rolename.lower() == 'gpl users':
                        data['DepartmentId'] = data['DepartmentId']
                    else:
                        data['DepartmentId'] = None
                else:
                    data['DepartmentId'] = None
            else:
                return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "Status": "Failed"}})
            serializer = UserSerializer(existemp,data=data,partial=True)
            emailObject = User.objects.filter(email__in = [email.strip().capitalize(),email.strip(),email.title()],isActive__in=[True]).exclude(id=userid).first()
            mobObject = User.objects.filter(mobileNumber = mobileNumber,isActive__in=[True]).exclude(id=userid).first()
            if emailObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this email id already exist","status": "failure"}})
            elif mobObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this mobile number already exist","status": "failure"}})
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
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "user updated successfully","status": "success"}})
                else:
                    return Response({"data":serializer.errors,"response": {"n": 0, "msg": "user not added ","status": "failure"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "user not found ","status": "failure"}})



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
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "user deleted successfully","status": "success"}})
            else:
                return Response({"data":serializer.errors,"response": {"n": 0, "msg": "user not deleted ","status": "failure"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "user not found ","status": "failure"}})


            
            
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
                'status':'failed',
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
                'status':'failed',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

# mappinguserlist=[1,2,3]
class addprojectmapping(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        projectid = request.data.get('ProjectId')
        print("projectid",projectid)
        if projectid is not None and projectid != "":
            projectobj = Project.objects.filter(id=int(projectid)).first()
            if projectobj is not None:
                mappinguserlist = request.data.get('mappinguserlist')
                checkifexist = ProjectMapping.objects.filter(projectid=int(projectid)).delete()
                for d in mappinguserlist:
                    ProjectMapping.objects.create(projectid=int(projectid),userid=str(d))

                response_={
                    'status':'success',
                    'msg':'Mapping Added Successfully.',
                    'data':''
                }
                return Response(response_,status=200)
            else:
                response_={
                'status':'failed',
                'msg':'Project not found.',
                'data':{}
            }
            return Response(response_,status=200)

        else:
            response_={
                'status':'failed',
                'msg':'Please Provide Project Id.',
                'data':{}
            }
            return Response(response_,status=200)


class listprojectmapping(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        Projectid =  request.data.get('ProjectId')
        cclist = []
        # designlist = []
        # operationlist = []
        # budgetinglist = []
        # planninglist = []
        # Auditorlist = []
        if Projectid is not None and Projectid != "":
            projectobj = Project.objects.filter(id=int(Projectid)).first()
            if projectobj is not None:
                userlist = ProjectMapping.objects.filter(projectid=int(Projectid)).order_by('id')
                if userlist.exists():
                    projectSerializer = ProjectMappingSerializer(userlist,many=True)
                    for i in projectSerializer.data:
                        userobj = User.objects.filter(id=str(i['userid'])).first()
                        if userobj is not None:
                            i['Username']=userobj.Username
                            userrole = userobj.role_id
                            roleobj = Role.objects.filter(id=int(userrole),isActive=True).first()
                            if roleobj is not None:
                                rolename = roleobj.RoleName
                            else:
                                rolename = ""

                            if rolename.lower() == 'auditor':
                                i['Depart'] = 'Audit'
                            elif rolename.lower() == 'gpl users':
                                userDept = userobj.DepartmentId
                                deptobj = Departments.objects.filter(id=userDept).first()
                                if deptobj is not None:
                                    i['Depart'] = deptobj.DepartmentName
                                else:
                                    i['Depart'] = ''
                            else:
                                i['Depart'] = ''
                            
                            cclist.append(i)
                          


                    context = {
                        'cclist':cclist,
                    }
                    
                    response_={
                        'status':'success',
                        'msg':'project Mapping list found  Successfully.',
                        'data':context
                    }
                    return Response(response_,status=200)
                else:
                    response_={
                    'status':'failed',
                    'msg':'Project mapping not found.',
                    'data':{}
                    }
                    return Response(response_,status=200)
            else:
                response_={
                'status':'failed',
                'msg':'Project not found.',
                'data':{}
            }
            return Response(response_,status=200)

        else:
            response_={
                'status':'failed',
                'msg':'Please Provide Project Id.',
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
            for c in ccUserser.data:
                deptobj = Departments.objects.filter(id=c['DepartmentId']).first()
                if deptobj is not None:
                    c['Depart'] = deptobj.DepartmentName
                else:
                    c['Depart'] = ''
                cclist.append(c)
        
        auditobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='Auditor')).order_by('id')
        if auditobjs.exists():
            auditUserser = UserSerializer(auditobjs,many=True)
            for a in auditUserser.data:
                a['Depart'] = 'Auditor'
                cclist.append(a)

        # designuserobjs = User.objects.filter(isActive=True,role= 3,DepartmentId = 2).order_by('id')
        # if designuserobjs.exists():
        #     designUserser = UserSerializer(designuserobjs,many=True)
        #     designlist = designUserser.data
        
        # opsuserobjs = User.objects.filter(isActive=True,role= 3,DepartmentId = 3).order_by('id')
        # if opsuserobjs.exists():
        #     opsUserser = UserSerializer(opsuserobjs,many=True)
        #     operationlist = opsUserser.data

        # budgetinguserobjs = User.objects.filter(isActive=True,role= 3,DepartmentId = 4).order_by('id')
        # if budgetinguserobjs.exists():
        #     budgetingUserser = UserSerializer(budgetinguserobjs,many=True)
        #     budgetinglist = budgetingUserser.data


        # planuserobjs = User.objects.filter(isActive=True,DepartmentId = 5,role= 3).order_by('id')
        # if planuserobjs.exists():
        #     planningUserser = UserSerializer(planuserobjs,many=True)
        #     planninglist = planningUserser.data


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