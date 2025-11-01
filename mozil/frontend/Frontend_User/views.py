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
from django.http import JsonResponse
from PaymentHistory.models import PaymentTransaction,PaymentTransactionErrorLog


# from Users.context_processers import ImageURL as imageURL
login_url=hosturl+"/api/User/login"
logout_url=hosturl+"/api/User/logout"
forgot_password_url=hosturl+"/api/User/forgetpasswordmail"
get_parent_services_list_url=hosturl+"/api/Services/parentservicelist"
get_child_services_list_url=hosturl+"/api/Services/childservicelist"
add_service_provider_url=hosturl+"/api/User/create_new_service_provider"
get_service_provider_details_url=hosturl+"/api/User/get_service_provider_details"
edit_service_provider_url=hosturl+"/api/User/update_service_provider_basic_details"
get_regions_list_url=hosturl+"/api/Masters/region_list"

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

def users_list(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'Users/users_list.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.

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
            get_regions_request = requests.get(get_regions_list_url,headers=headers)
            get_regions_response = get_regions_request.json()
            return render(request, 'ServiceProvider/add_service_provider.html',{'parent_services':get_parent_service_response['data'],'child_services':get_child_service_response['data'],'regions':get_regions_response['data']})
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
            get_regions_request = requests.get(get_regions_list_url,headers=headers)
            get_regions_response = get_regions_request.json()
            get_service_provider_details_request = requests.post(get_service_provider_details_url,data=data,headers=headers)
            get_service_provider_details_response = get_service_provider_details_request.json()
            return render(request, 'ServiceProvider/edit_service_provider.html',{'parent_services':get_parent_service_response['data'],'child_services':get_child_service_response['data'],'obj':get_service_provider_details_response['data'],'regions':get_regions_response['data']})
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
    

def privacy_policy(request):


    return render(request, 'info/privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'info/terms-and-conditions.html')

@csrf_exempt
def test_logger(request):
    PaymentTransactionErrorLog.objects.create(error="Webhook test OK")
    return JsonResponse({"status": "logged"})


@csrf_exempt
def mips_imn_callback(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid"}, status=400)

    try:
        # Parse raw body safely
        body_text = request.body.decode("utf-8")
        print("RAW BODY:", body_text)

        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            PaymentTransactionErrorLog.objects.create(
                error=f"Invalid JSON received: {body_text}"
            )
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

        crypted_callback = body.get("crypted_callback")
        if not crypted_callback:
            PaymentTransactionErrorLog.objects.create(
                error=f"Missing crypted_callback in body: {body_text}"
            )
            return JsonResponse({"status": "error", "message": "crypted_callback missing"}, status=400)

        # Build decrypt payload
        decrypt_payload = {
            "authentify": {
                "id_merchant": "QTly9lr7DpFDTCKoQkhA6LSxNifIKYM4",
                "id_entity": "wKmuyCkYnpB2LI5G9tuO7AAZdR1vLol4",
                "id_operator": "zoBS7fcd5I5sMW6o4bf6zUuwHme5VNuN",
                "operator_password": "eGocxH8e7KFXCpTcTJr4zyauqdtvv6VG"
            },
            "salt": "NW4o3lkw5ZudvFc3TlbcaY4LDDyiPkE5ipHbmgDU6U0C7pYSN3",
            "cipher_key": "Zlm85vMwefbmpMq0IyvSP6bKlUBLoBGx98OLhYeUnAIyZQI37pPCKuq3hzMyrb51r8xd83pD1oSZNUUOI19nsS6LyQWj9MXdkqge",
            "received_crypted_data": crypted_callback
        }

        # Call decrypt API
        decrypt_response = requests.post(
            "https://api.mips.mu/api/decrypt_imn_data",
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            auth=("mozil_our_island_guide_f1952a", "5adb68ba33e46fffae0ac3292cd250d6"),
            json=decrypt_payload
        )

        print("MIPS DECRYPT RESPONSE STATUS:", decrypt_response.status_code)
        print("MIPS DECRYPT RAW:", decrypt_response.text)

        # Parse JSON
        try:
            decrypted = decrypt_response.json()
        except Exception as e:
            PaymentTransactionErrorLog.objects.create(
                error=f"Failed to parse decrypt response: {str(e)} | Raw: {decrypt_response.text}"
            )
            return JsonResponse({"status": "error"}, status=500)

        # If MiPS returns failure, log it
        if not isinstance(decrypted, dict) or decrypted.get("status") == "fail":
            PaymentTransactionErrorLog.objects.create(
                error=f"Decrypt API failed or returned invalid structure: {json.dumps(decrypted)}"
            )
            return JsonResponse({"status": "error"}, status=400)

        # Extract fields safely
        order_id = decrypted.get("id_order")
        amount = decrypted.get("amount")
        currency = decrypted.get("currency")
        status = decrypted.get("status")
        transaction_id = decrypted.get("transaction_id")
        payment_method = decrypted.get("payment_method")

        # If required fields are missing, log error
        if not order_id:
            PaymentTransactionErrorLog.objects.create(
                error=f"Missing order_id in decrypted response: {json.dumps(decrypted)}"
            )
            return JsonResponse({"status": "error"}, status=400)

        # ✅ Create transaction record
        PaymentTransaction.objects.create(
            order_id=order_id,
            amount=float(amount or 0) / 100,
            currency=currency,
            status=status,
            transaction_id=transaction_id,
            payment_method=payment_method,
            raw_data=decrypted
        )

        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        PaymentTransactionErrorLog.objects.create(
            error=f"Unhandled exception: {str(e)}"
        )
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    if request.method != "POST":
        return JsonResponse({"status": "invalid"}, status=400)

    try:
        # Parse body safely
        body_text = request.body.decode("utf-8")
        print("RAW BODY:", body_text)
        
        try:
            body = json.loads(body_text)
        except json.JSONDecodeError:
            body = {}
        
        crypted_callback = body.get("crypted_callback")
        if not crypted_callback:
            return JsonResponse({"error": "crypted_callback missing or invalid body"}, status=400)

        # Build decrypt payload
        decrypt_payload = {
            "authentify": {
                "id_merchant": "QTly9lr7DpFDTCKoQkhA6LSxNifIKYM4",
                "id_entity": "wKmuyCkYnpB2LI5G9tuO7AAZdR1vLol4",
                "id_operator": "zoBS7fcd5I5sMW6o4bf6zUuwHme5VNuN",
                "operator_password": "eGocxH8e7KFXCpTcTJr4zyauqdtvv6VG"
            },
            "salt": "NW4o3lkw5ZudvFc3TlbcaY4LDDyiPkE5ipHbmgDU6U0C7pYSN3",
            "cipher_key": "Zlm85vMwefbmpMq0IyvSP6bKlUBLoBGx98OLhYeUnAIyZQI37pPCKuq3hzMyrb51r8xd83pD1oSZNUUOI19nsS6LyQWj9MXdkqge",
            "received_crypted_data": crypted_callback
        }

        # Call decrypt API
        decrypt_response = requests.post(
            "https://api.mips.mu/api/decrypt_imn_data",
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            auth=("mozil_our_island_guide_f1952a", "5adb68ba33e46fffae0ac3292cd250d6"),
            json=decrypt_payload
        )

        print("MIPS DECRYPT RESPONSE STATUS:", decrypt_response.status_code)
        print("MIPS DECRYPT RAW:", decrypt_response.text)

        # Try to parse JSON
        try:
            decrypted = decrypt_response.json()
        except Exception:
            decrypted = {"raw": decrypt_response.text}

        if not isinstance(decrypted, dict):
            decrypted = {"raw": decrypted}

        # Handle nested or missing structure
        order_id = decrypted.get("id_order") or decrypted.get("data", {}).get("id_order")
        amount = decrypted.get("amount") or decrypted.get("data", {}).get("amount")
        currency = decrypted.get("currency") or decrypted.get("data", {}).get("currency")
        status = decrypted.get("status") or decrypted.get("data", {}).get("status")
        transaction_id = decrypted.get("transaction_id") or decrypted.get("data", {}).get("transaction_id")
        payment_method = decrypted.get("payment_method") or decrypted.get("data", {}).get("payment_method")

        # ✅ Save only if decrypted looks valid
        if order_id:
            PaymentTransaction.objects.create(
                order_id=order_id,
                amount=float(amount or 0) / 100,
                currency=currency,
                status=status,
                transaction_id=transaction_id,
                payment_method=payment_method,
                raw_data=decrypted
            )

        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        print("IMN Error:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)