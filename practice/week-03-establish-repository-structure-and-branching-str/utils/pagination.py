"""
Custom pagination classes standardizing JSON API envelopes.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class providing consistent envelope structure:
    {
        "success": true,
        "pagination": {
            "count": 42,
            "total_pages": 5,
            "current_page": 1,
            "next": "...",
            "previous": null
        },
        "results": [...]
    }
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "pagination": {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "results": data,
        })
