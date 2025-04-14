from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.exceptions import ValidationError

from .serializers import CampaignSerializer, CampaignEditSerializer, CampaignImageSerializer
from advertisers.models import Advertiser
from .models import Campaign
from .paginations import CampaignPagination

from django.shortcuts import get_object_or_404

from ad_platform.settings.base import giga

import logging

class CampaignsView(APIView, CampaignPagination):
    def post(self, request, advertiser_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        request.data["advertiser_id"] = advertiser.advertiser_id
        serializer = CampaignSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            response = serializer.create(serializer.validated_data)
            return Response(response, status=status.HTTP_201_CREATED)
            # return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
        logging.critical(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, advertiser_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        campaigns = advertiser.campaigns.order_by('campaign_id')
        results = self.paginate_queryset(campaigns, request, view=self)
        serializer = CampaignSerializer(results, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

class CampaignGenerateTextView(APIView):
    def post(self, request, advertiser_id, format=None):
        if "ad_title" not in request.data:
            raise ValidationError("ad_title is required")
        additive_data = request.data.get("about_campaign", "")
        response = giga.chat(f"Сгенерируй описание для рекламной кампании с названием {request.data['ad_title']}. Также учитывай это: {additive_data}. В ответе просто верни описание. Без empdji и markdown")
        return Response({"generated_text": response.choices[0].message.content}, status=status.HTTP_200_OK)

class CampaignView(APIView):
    def get(self, request, advertiser_id, campaign_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        serializer = CampaignSerializer(campaign, context={"request": request})
        return Response(serializer.data)

    def put(self, request, advertiser_id, campaign_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        old_request_data = request.data.copy()
        request.data["advertiser_id"] = advertiser_id
        request.data["campaign_id"] = campaign_id
        serializer = CampaignEditSerializer(campaign, data=request.data)
        if serializer.is_valid():
            serializer.update(serializer.validated_data, campaign_id=campaign_id, request_data=old_request_data)
            response = CampaignSerializer(get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id), context={"request": request}).data
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, advertiser_id, campaign_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        images = campaign.images.all()
        for image in images:
            image.delete()
        campaign.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class CampaignImagesView(APIView, CampaignPagination):
    def get(self, request, advertiser_id, campaign_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        images = campaign.images.order_by('id')
        results = self.paginate_queryset([{"id": image.id, "url": request.build_absolute_uri(image.image.url)} for image in images], request, view=self)
        return self.get_paginated_response(results)

    def post(self, request, advertiser_id, campaign_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        request.data["campaign"] = campaign.campaign_id
        serializer = CampaignImageSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.create(serializer.validated_data)
            return Response({"url": request.build_absolute_uri(data.image.url)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageView(APIView):
    def delete(self, request, advertiser_id, campaign_id, image_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        image = get_object_or_404(campaign.images, id=image_id)
        image.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, advertiser_id, campaign_id, image_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id, advertiser_id=advertiser_id)
        image = get_object_or_404(campaign.images, id=image_id)
        return Response({"url": request.build_absolute_uri(image.image.url)}, status=status.HTTP_200_OK)