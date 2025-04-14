from rest_framework import serializers
from .models import Advertiser, MLScore

class AdvertiserSerializer(serializers.ModelSerializer):
    advertiser_id = serializers.CharField(max_length=100)
    class Meta:
        model = Advertiser
        fields = ["advertiser_id", "name"]

    def create(self, validated_data):
        advertiser, created = Advertiser.objects.update_or_create(
            advertiser_id=validated_data.get('advertiser_id'),
            defaults={'name': validated_data.get('name')}
        )
        return advertiser

class MLScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLScore
        fields = ["advertiser_id", "client_id", "score"]

    def create(self, validated_data):
        ml_score, created = MLScore.objects.update_or_create(
            advertiser_id=validated_data.get('advertiser_id'),
            client_id=validated_data.get('client_id'),
            defaults={'score': validated_data.get('score')}
        )
        return ml_score