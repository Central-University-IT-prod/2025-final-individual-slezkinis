from rest_framework import serializers
from .models import Client

import logging

class ClientSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(max_length=100)
    class Meta:
        model = Client
        fields = ["login", "age", "location", "gender", "client_id"]

    def create(self, validated_data):
        client_id = validated_data.get('client_id')
        if Client.objects.filter(client_id=client_id).exists():
            client = Client.objects.get(client_id=client_id)
            client.login = validated_data.get('login')
            client.age = validated_data.get('age')
            client.location = validated_data.get('location')
            client.gender = validated_data.get('gender')
            client.save()
        else:
            client = Client.objects.create(**validated_data)
        return client
