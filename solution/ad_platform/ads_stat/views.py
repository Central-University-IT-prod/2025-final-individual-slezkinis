from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.cache import cache

from campaigns.models import Campaign
from advertisers.models import Advertiser

class CampaignStatsView(APIView):
    def get(self, request, campaign_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
        immersive_count = campaign.views.all().count()
        clicks_count = campaign.clicks.all().count()
        spent_impressions = sum([view.price for view in campaign.views.all()])
        spent_clicks = sum([click.price for click in campaign.clicks.all()])
        response = {
            "immersive_count": immersive_count,
            "clicks_count": clicks_count,
            "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks,
            "total": spent_impressions + spent_clicks
        }
        return Response(response, status=status.HTTP_200_OK)


class AdvertiserStatsView(APIView):
    def get(self, request, advertiser_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        campaigns = advertiser.campaigns.all()
        immersive_count = sum([campaign.views.all().count() for campaign in campaigns])
        clicks_count = sum([campaign.clicks.all().count() for campaign in campaigns])
        spent_impressions = sum([view.price for campaign in campaigns for view in campaign.views.all()])
        spent_clicks = sum([click.price for campaign in campaigns for click in campaign.clicks.all()])
        response = {
            "immersive_count": immersive_count,
            "clicks_count": clicks_count,
            "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
            "spent_impressions": spent_impressions,
            "spent_clicks": spent_clicks,
            "total": spent_impressions + spent_clicks
        }
        return Response(response, status=status.HTTP_200_OK)


class CampaignsStatsDailyView(APIView):
    def get(self, request, campaign_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=campaign_id)
        now = cache.get('time', 0)
        response = []
        for time in range(0, now + 1):
            immersive_count = campaign.views.filter(date=time).count()
            clicks_count = campaign.clicks.filter(date=time).count()
            spent_impressions = sum([view.price for view in campaign.views.filter(date=time)])
            spent_clicks = sum([click.price for click in campaign.clicks.filter(date=time)])
            response_for_date = {
                "immersive_count": immersive_count,
                "clicks_count": clicks_count,
                "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
                "spent_impressions": spent_impressions,
                "spent_clicks": spent_clicks,
                "total": spent_impressions + spent_clicks,
                "date": time
            }
            response.append(response_for_date)
        return Response(response, status=status.HTTP_200_OK)



class AdvertisersStatsDailyView(APIView):
    def get(self, request, advertiser_id, format=None):
        advertiser = get_object_or_404(Advertiser, advertiser_id=advertiser_id)
        now = cache.get('time', 0)
        response = []
        for time in range(0, now + 1):
            immersive_count = sum([campaign.views.filter(date=time).count() for campaign in advertiser.campaigns.all()])
            clicks_count = sum([campaign.clicks.filter(date=time).count() for campaign in advertiser.campaigns.all()])
            spent_impressions = sum([view.price for campaign in advertiser.campaigns.all() for view in campaign.views.filter(date=time)])
            spent_clicks = sum([click.price for campaign in advertiser.campaigns.all() for click in campaign.clicks.filter(date=time)])
            response_for_date = {
                "immersive_count": immersive_count,
                "clicks_count": clicks_count,
                "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0,
                "spent_impressions": spent_impressions,
                "spent_clicks": spent_clicks,
                "total": spent_impressions + spent_clicks,
                "date": time
            }
            response.append(response_for_date)
        return Response(response, status=status.HTTP_200_OK)