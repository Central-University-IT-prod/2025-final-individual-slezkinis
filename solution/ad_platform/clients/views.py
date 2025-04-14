from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from django.shortcuts import get_object_or_404

from .models import Client
from .serializers import ClientSerializer



class ClientView(APIView):
    def get(self, request, client_id, format=None):
        print(1)
        client = get_object_or_404(Client, client_id=client_id)
        serializer = ClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientsCreateView(APIView):
    def post(self, request, format=None):
        serializer = ClientSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


