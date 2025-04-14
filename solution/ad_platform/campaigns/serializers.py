from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from django.core.cache import cache

from .models import Campaign, CampaignImage

from uuid import uuid4

from .utils import is_bad

import logging

class CampaignTargetSerializer(ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "gender",
            "age_from",
            "age_to",
            "location"
        ]

    
class CampaignSerializer(ModelSerializer):
    targeting = CampaignTargetSerializer(required=False)
    class Meta:
        model = Campaign
        fields = [
            "advertiser_id",
            "impressions_limit",
            "clicks_limit",
            "cost_per_impression",
            "cost_per_click",
            "ad_title",
            "ad_text",
            "start_date",
            "end_date",
            "targeting"
        ]

    def validate(self, data):
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise serializers.ValidationError("Start date must be less than end date")
        if start_date is None and start_date <= cache.get('time', 0):
            raise serializers.ValidationError("Start date must be greater than current time")
        if end_date is None and end_date <= cache.get('time', 0):
            raise serializers.ValidationError("End date must be greater than current time")
        moderation_status = cache.get('censor_status', False)
        logging.error(moderation_status)
        if moderation_status:
            if not is_bad(data.get('ad_title', None)) or not is_bad(data.get('ad_text', None)):
                raise serializers.ValidationError("Ad title or ad text contains bad words")
        try:
            targer = self.initial_data.pop('targeting')
        except KeyError:
            targer = {}
        data['targeting'] = targer
        return data

    def create(self, validated_data):
        old_validated_data = validated_data.copy()
        old_validated_data["advertiser_id"] = validated_data["advertiser_id"].advertiser_id
        try:
            target = validated_data.pop('targeting')
        except KeyError:
            target = {}
        new_dict = {**validated_data, **target}
        new_dict["campaign_id"] = str(uuid4())
        campaign = Campaign.objects.create(**new_dict)
        old_validated_data["campaign_id"] = campaign.campaign_id
        return old_validated_data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['targeting'] = {}
        if instance.gender is not None:
            representation['targeting']['gender'] = instance.gender
        if instance.age_from is not None:
            representation['targeting']['age_from'] = instance.age_from
        if instance.age_to is not None:
            representation['targeting']['age_to'] = instance.age_to
        if instance.location is not None:
            representation['targeting']['location'] = instance.location
        request = self.context.get("request")
        images = [{"id": image.id, "url": request.build_absolute_uri(image.image.url)} for image in instance.images.all()]
        if images:
            representation["images"] = images
        representation["campaign_id"] = instance.campaign_id
        return representation


class CampaignEditSerializer(ModelSerializer):
    targeting = CampaignTargetSerializer(required=False, default=None)
    impressions_limit = serializers.IntegerField(default=None)
    clicks_limit = serializers.IntegerField(default=None)
    start_date = serializers.IntegerField(default=None)
    end_date = serializers.IntegerField(default=None)
    cost_per_impression = serializers.FloatField(required=False, default=None)
    cost_per_click = serializers.FloatField(required=False, default=None)
    ad_title = serializers.CharField(required=False, default=None)
    ad_text = serializers.CharField(required=False, default=None)
    class Meta:
        model = Campaign
        fields = [
            "advertiser_id",
            "impressions_limit",
            "clicks_limit",
            "cost_per_impression",
            "cost_per_click",
            "ad_title",
            "ad_text",
            "start_date",
            "end_date",
            "targeting"
        ]
        
    def validate(self, data):
        campaign = self.instance
        if data["impressions_limit"] is None or data["impressions_limit"] != campaign.impressions_limit:
            raise serializers.ValidationError("You can't change impressions limit")
        if data["clicks_limit"] is None or data["clicks_limit"] != campaign.clicks_limit:
            raise serializers.ValidationError("You can't change clicks limit")
        if data["start_date"] is None or data["start_date"] != campaign.start_date:
            raise serializers.ValidationError("You can't change start date")
        if data["end_date"] is None or data["end_date"] != campaign.end_date:
            raise serializers.ValidationError("You can't change end date")
        moderation_status = cache.get('censor_status', False)
        if moderation_status:
            if not is_bad(data.get('ad_title', None)) or not is_bad(data.get('ad_text', None)):
                raise serializers.ValidationError("Ad title or ad text contains bad words")
        try:
            targer = self.initial_data.pop('targeting')
        except KeyError:
            targer = {}
        data['targeting'] = targer
        return data


    def update(self, validated_data, campaign_id, request_data):
        old_validated_data = validated_data.copy()
        old_validated_data["advertiser_id"] = validated_data["advertiser_id"].advertiser_id
        old_campaign = Campaign.objects.get(campaign_id=campaign_id)
        target = validated_data.pop('targeting')
        if "targeting" not in request_data or target is None:
            new_target = {
                "gender": None,
                "age_from": None,
                "age_to": None,
                "location": None
            }
        else:
            new_target = {
                "gender": target.get("gender", None),
                "age_from": target.get("age_from", None),
                "age_to": target.get("age_to", None),
                "location": target.get("location", None)
            }
        new_dict = {**validated_data, **new_target}
        try:
            campaign = Campaign.objects.filter(campaign_id=campaign_id).update(**new_dict)
        except:
            raise serializers.ValidationError("Required fields not found")
        old_validated_data["campaign_id"] = campaign_id
        return old_validated_data


class CampaignImageSerializer(ModelSerializer):
    class Meta:
        model = CampaignImage
        fields = ["image", "campaign"]

    def create(self, validated_data):
        campaign_image = CampaignImage.objects.create(**validated_data)
        return campaign_image
