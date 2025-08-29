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
add_plan_url=hosturl+"/api/Plans/addplan"
edit_plan_url=hosturl+"/api/Plans/updateplan"
get_plan_url=hosturl+"/api/Plans/planbyid"
get_plans_list_url=hosturl+"/api/Plans/planlist"

# Create your views here.
def service_provider_purchase_history(request):
    token = request.session.get('token',False)
    if token:

        return render(request, 'PaymentHistory/payment_history.html')
    else:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('Frontend_User:login') # change this.
    


# views.py
# PaymentHistory/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import hashlib
import json

# def payment_page(request):
#     """
#     Display payment page with embedded MIPS payment frame
#     """
#     # These values should be provided by MIPS
#     merchant_id = "QTly9lr7DpFDTCKoQkhA6LSxNifIKYM4"
#     form_id = "1234"
#     salt = "NW4o3lkw5ZudvFc3TlbcaY4LDDyiPkE5ipHbmgDU6U0C7pYSN3"
#     cipher_key = "Zlm85vMwefbmpMq0IyvSP6bKlUBLoBGx98OLhYeUnAIyZQI37pPCKuq3hzMyrb51r8xd83pD1oSZNUUOI19nsS6LyQWj9MXdkqge"
    
#     # Order details (in a real app, these would come from your database)
#     order_id = "ORDER_" + str(request.session.get('order_id', '12345'))
#     amount = 25000  # Amount in cents (250.00 EUR)
#     currency = "EUR"  # Currency code
    
#     # Generate checksum for security
#     checksum_data = f"{amount}{currency}{salt}"
#     checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
    
#     # Construct the payment URL (get actual URL format from MIPS docs)
#     base_url = "https://payment.mips.mu/process"

#     payment_url = (
#         f"{base_url}?id_merchant={merchant_id}&"
#         f"id_form={form_id}&id_order={order_id}&"
#         f"amount={amount}&currency={currency}&"
#         f"checksum={checksum}"
#     )
#     print("payment_url",payment_url)

    


#     crypted = "ENCRYPTED_STRING_FROM_API"

#     mips_url = f"https://secure.mips.mu/payment.php?crypted={crypted}"
#     context = {
#         'payment_url': mips_url,
#         'order_id': order_id,
#         'amount': amount / 100,  # Convert to dollars/euros
#         'currency': currency,
#         'mips_url': mips_url
#     }
#     return render(request, 'PaymentHistory/payment_page.html', context)

from requests.auth import HTTPBasicAuth

def payment_page(request):
    """
    Display payment page with embedded MIPS payment frame
    """

    # MIPS Credentials
    merchant_id = "QTly9lr7DpFDTCKoQkhA6LSxNifIKYM4"
    entity_id = "wKmuyCkYnpB2LI5G9tuO7AAZdR1vLol4"
    operator_id = "zoBS7fcd5I5sMW6o4bf6zUuwHme5VNuN"
    operator_password = "eGocxH8e7KFXCpTcTJr4zyauqdtvv6VG"
    salt = "NW4o3lkw5ZudvFc3TlbcaY4LDDyiPkE5ipHbmgDU6U0C7pYSN3"
    cipher_key = "Zlm85vMwefbmpMq0IyvSP6bKlUBLoBGx98OLhYeUnAIyZQI37pPCKuq3hzMyrb51r8xd83pD1oSZNUUOI19nsS6LyQWj9MXdkqge"

    # Order Info
    order_id = "ORDER_" + str(request.session.get('order_id', '12345'))
    amount = 25000  # in cents
    currency = "EUR"
    callback_url = "https://yourdomain.com/payment/callback"

    # API Payload to generate crypted
    payload = {
        "authentify": {
            "id_merchant": merchant_id,
            "id_entity": entity_id,
            "id_operator": operator_id,
            "operator_password": operator_password
        },
        "salt": salt,
        "cipher_key": cipher_key,
        "payment_data": {
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "callback_url": callback_url
        }
    }

    # Make API call to get encrypted string
    try:
        response = requests.post(
            "https://api.mips.mu/api/encrypt_imn_data",  # ✅ CORRECT endpoint
            json=payload,
            auth=HTTPBasicAuth("mozil_our_island_guide_f1952a", "5adb68ba33e46fffae0ac3292cd250d6")
        )

        response.raise_for_status()
        crypted = response.json().get("crypted", "")
    except Exception as e:
        print("e",e)
        return render(request, 'PaymentHistory/payment_page.html', {
            'error': "Error generating MIPS payment link",
            'details': str(e)
        })

    # Final payment URL
    mips_url = f"https://secure.mips.mu/payment.php?crypted={crypted}"

    return render(request, 'PaymentHistory/payment_page.html', {
        'mips_url': mips_url,
        'order_id': order_id,
        'amount': amount / 100,  # convert to major units
        'currency': currency
    })




@csrf_exempt
def payment_callback(request):
    """
    Handle payment callback from MIPS
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")
    
    # Get values from MIPS (these should be provided by MIPS)
    salt = 'A_UNIQUE_KEY'
    cipher_key = 'A_SECOND_UNIQUE_KEY'
    
    try:
        # Extract data from callback (adjust based on MIPS actual format)
        crypted_data = request.POST.get('crypted_callback')
        id_order = request.GET.get('id_order')
        amount = request.POST.get('amount')  # in cents
        currency = request.POST.get('currency')
        status = request.POST.get('status')  # "success" or other status
        checksum = request.POST.get('checksum')
        
        # Verify checksum
        checksum_data = hashlib.sha256(f"{amount}{currency}{status}{salt}".encode()).hexdigest()
        
        if checksum != checksum_data:
            return HttpResponse("Invalid checksum", status=400)
        
        if status.lower() == "success":
            # Payment successful - update your database
            # Example:
            # order = Order.objects.get(order_id=id_order)
            # order.status = 'paid'
            # order.save()
            
            # You might also want to send confirmation emails here
            
            return HttpResponse("success")
        else:
            # Payment failed
            # order = Order.objects.get(order_id=id_order)
            # order.status = 'failed'
            # order.save()
            return HttpResponse("fail")
            
    except Exception as e:
        # Log the error for debugging
        # logger.error(f"Payment callback error: {str(e)}")
        return HttpResponse(f"Error processing payment: {str(e)}", status=500)
    
# PaymentHistory/views.py
def payment_success(request):
    """
    Display payment success page
    """
    # In a real app, you might want to verify the payment again here
    # or get order details from session/database
    
    context = {
        'order_id': request.session.get('order_id', 'N/A'),
    }
    return render(request, 'PaymentHistory/success.html', context)


