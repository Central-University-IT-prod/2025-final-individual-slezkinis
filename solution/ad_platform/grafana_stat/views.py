from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ads.models import View, Click

from django.core.cache import cache


class ClickImmersiveView(APIView):
    def get(self, request, format=None):
        clicks_count = Click.objects.all().count()
        immersive_count = View.objects.all().count()
        return Response({
            "clicks_count": clicks_count,
            "immersive_count": immersive_count
        }, status=status.HTTP_200_OK)


class ClickImmersiveDailyView(APIView):
    def get(self, request, format=None):
        now = cache.get('time', 0)
        response = []
        for time in range(0, now + 1):
            clicks_count = Click.objects.filter(date=time).count()
            immersive_count = View.objects.filter(date=time).count()
            response_for_date = {
                "clicks_count": clicks_count,
                "immersive_count": immersive_count,
                "date": time
            }
            response.append(response_for_date)
        return Response(response, status=status.HTTP_200_OK)

class CostImmersiveClicksDailyView(APIView):
    def get(self, request, format=None):
        now = cache.get('time', 0)
        response = []
        for time in range(0, now + 1):
            clicks_count = Click.objects.filter(date=time).count()
            immersive_count = View.objects.filter(date=time).count()
            spent_impressions = sum([view.price for view in View.objects.filter(date=time)])
            spent_clicks = sum([click.price for click in Click.objects.filter(date=time)])
            response_for_date = {
                "clicks_count": clicks_count,
                "immersive_count": immersive_count,
                "spent_impressions": spent_impressions,
                "spent_clicks": spent_clicks,
                "total": spent_impressions + spent_clicks,
                "date": time
            }
            response.append(response_for_date)
        return Response(response, status=status.HTTP_200_OK)


class TotalProfitView(APIView):
    def get(self, request, format=None):
        spent_impressions = sum([view.price for view in View.objects.all()])
        spent_clicks = sum([click.price for click in Click.objects.all()])
        return Response({
            "total": spent_impressions + spent_clicks
        }, status=status.HTTP_200_OK)


class TotalConversationView(APIView):
    def get(self, request, format=None):
        clicks_count = Click.objects.all().count()
        immersive_count = View.objects.all().count()
        return Response({
            "conversion": round(clicks_count / immersive_count * 100, 2) if immersive_count != 0 else 0
        }, status=status.HTTP_200_OK)