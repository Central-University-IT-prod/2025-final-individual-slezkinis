from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from campaigns.models import Campaign
from clients.models import Client

from .models import Click


class AdSerializer(serializers.ModelSerializer):
    ad_id = serializers.CharField(source="campaign_id")
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        images = obj.images.all()
        return [{"url": image.image.url} for image in images]


    class Meta:
        model = Campaign
        fields = [
            "advertiser_id",
            "ad_id",
            "ad_title",
            "ad_text",
            "images",
        ]

class ClickSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(max_length=100)
    class Meta:
        model = Client
        fields = [
            "client_id",
        ]

    def create(self, validated_data, now, campaign):
        try:
            client = Client.objects.get(client_id=validated_data["client_id"])
        except:
            return ValidationError("Client not found")
        try:
            click = Click.objects.create(campaign=campaign, client=client, date=now, price=campaign.cost_per_click)
        except:
            pass