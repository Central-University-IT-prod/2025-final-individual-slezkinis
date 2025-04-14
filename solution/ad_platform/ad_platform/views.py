# import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.cache import cache


class TimeView(APIView):
    def post(self, request, format=None):
        if "current_date" not in request.data:
            return Response({"error": "current_date is required"}, status=status.HTTP_400_BAD_REQUEST)
        cache.set('time', request.data['current_date'])
        return Response(request.data, status=status.HTTP_201_CREATED)