from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.cache import cache


from campaigns.models import Campaign
from clients.models import Client
from advertisers.models import MLScore

from .serializers import AdSerializer, ClickSerializer
from .models import View, Click


# TODO Test it
class AdsView(APIView):
    def get(self, request, format=None):
        try:
            time = cache.get('time', 0)
            client = get_object_or_404(Client, client_id=request.query_params.get('client_id'))
            campaigns_row = Campaign.objects.filter(start_date__lte=time, end_date__gte=time)
            campaigns = []
            for campaign in campaigns_row:
                is_target_ok = (campaign.gender == client.gender or campaign.gender is None or campaign.gender == 'ALL') and (campaign.age_from is None or campaign.age_from <= client.age) and (campaign.age_to is None or campaign.age_to >= client.age) and (campaign.location == client.location or campaign.location is None)
                try:
                    ml_score = MLScore.objects.filter(advertiser_id=campaign.advertiser_id, client_id=client.client_id).first().score
                except:
                    ml_score = 0
                if not is_target_ok:
                    continue
                viewed = View.objects.filter(campaign=campaign, client=client, date=time).exists()
                clicked = Click.objects.filter(campaign=campaign, client=client, date=time).exists()
                if viewed and clicked:
                    continue
                count_view = View.objects.filter(campaign=campaign).count()
                # count_click = Click.objects.filter(campaign=campaign).count()
                score = 0.6 * (campaign.cost_per_impression if not viewed else 0) + 0.6 * (campaign.cost_per_click if not clicked else 0) + 0.1 * ml_score + 0.2 * (max([campaign.cost_per_impression, campaign.cost_per_click]) if count_view / campaign.impressions_limit < 0.7 else 0)
                campaigns.append((campaign, score))
            if campaigns:
                maximum_related_campaign = max(campaigns, key=lambda x: x[1])[0]
                try:
                    View.objects.create(campaign=maximum_related_campaign, client=client, date=time, price=maximum_related_campaign.cost_per_impression)
                except:
                    pass
                return Response(AdSerializer(maximum_related_campaign).data, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


class ClickView(APIView):
    def post(self, request, ad_id, format=None):
        campaign = get_object_or_404(Campaign, campaign_id=ad_id)
        serializer = ClickSerializer(data=request.data)
        now = cache.get('time', 0)
        if serializer.is_valid():
            serializer.create(serializer.validated_data, now, campaign)
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)