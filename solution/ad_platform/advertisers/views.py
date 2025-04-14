from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Advertiser
from .serializers import AdvertiserSerializer, MLScoreSerializer


class AdvertisersGetView(APIView):
    def get(self, request, advertiser_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        serializer = AdvertiserSerializer(advertiser)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisersCreateView(APIView):
    def post(self, request, format=None):
        serializer = AdvertiserSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MLScoreView(APIView):
    def post(self, request, format=None):
        serializer = MLScoreSerializer(data=request.data, many=False)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)