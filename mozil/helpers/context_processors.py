import requests
from helpers.validations import hosturl

def get_session(request):
    token = request.session.get('token')
    # Menu = request.session.get('Menu')
    # Firstname = request.session.get('Firstname')
    # Lastname = request.session.get('Lastname')
    # Designation = request.session.get('Designation')
    # userID = request.session.get('userID')
    # userEmployeeId=request.session.get('userEmployeeId')
    # rules = request.session.get('rules')
    # roleID = request.session.get('roleID')
    # rolename = request.session.get('rolename')
    
    # companylogo = request.session.get('companylogo')
    # userphoto = request.session.get('userPhoto')
    # is_staff = request.session.get('is_staff')
    


   
    return {'token':token,'hosturl':hosturl
            }
