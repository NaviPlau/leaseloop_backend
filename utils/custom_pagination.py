import math

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """
        Returns a response object with paginated data.

        :param data: The serialized page objects
        :return: A response object with the following keys:
            - count: The total number of objects
            - total_pages: The total number of pages
            - next: The URL of the next page, or None
            - previous: The URL of the previous page, or None
            - results: The serialized page objects
        """
        total_pages = math.ceil(self.page.paginator.count / self.page_size)

        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

