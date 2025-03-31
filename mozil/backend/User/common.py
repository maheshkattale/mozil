from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def get_paginated_response(self,data):
        response = Response({
            'status':"success",
            'count':self.page.paginator.count,
            'next' : self.get_next_link(),
            'previous' : self.get_previous_link(),
            'data':data,
        })
     
        return response
    
    
class CustomDualPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def get_paginated_response(self,data):
        print("data",data)
        list1 = data.get('data', [])
        list2 = data.get('suggestions', [])
 
        # You can customize the response to include both lists and pagination metadata
        return Response({
            'count': self.page.paginator.count,  # Total number of items (use the appropriate count)
            'total_pages': self.page.paginator.num_pages,  # Total number of pages
            'current_page': self.page.number,  # Current page number
            'next' : self.get_next_link(),
            'previous' : self.get_previous_link(),
            'data': list1,
            'suggestions': list2,
        })
        
        
        # return response

