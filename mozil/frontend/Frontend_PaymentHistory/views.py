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
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import hashlib
import json

def payment_page(request):
    """
    Display payment page with embedded MIPS payment frame
    """
    # These values should be provided by MIPS
    merchant_id = "YOUR_MERCHANT_ID"
    form_id = "YOUR_FORM_ID"
    salt = "A_UNIQUE_KEY"
    cipher_key = "A_SECOND_UNIQUE_KEY"
    
    # Order details (in a real app, these would come from your database)
    order_id = "ORDER_" + str(request.session.get('order_id', '12345'))
    amount = 25000  # Amount in cents (250.00 EUR)
    currency = "EUR"  # Currency code
    
    # Generate checksum for security
    checksum_data = f"{amount}{currency}{salt}"
    checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
    
    # Construct the payment URL (get actual URL format from MIPS docs)
    base_url = "https://payment.mips.mu/process"
    payment_url = (
        f"{base_url}?id_merchant={merchant_id}&"
        f"id_form={form_id}&id_order={order_id}&"
        f"amount={amount}&currency={currency}&"
        f"checksum={checksum}"
    )
    print("payment_url",payment_url)
    context = {
        'payment_url': payment_url,
        'order_id': order_id,
        'amount': amount / 100,  # Convert to dollars/euros
        'currency': currency,
    }
    return render(request, 'PaymentHistory/payment_page.html', context)


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



