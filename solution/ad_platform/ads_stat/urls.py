from django.urls import path
from .views import CampaignStatsView, AdvertiserStatsView, CampaignsStatsDailyView, AdvertisersStatsDailyView


urlpatterns = [
    path("campaigns/<str:campaign_id>", CampaignStatsView.as_view()),
    path("advertisers/<str:advertiser_id>/campaigns", AdvertiserStatsView.as_view()),
    path("campaigns/<str:campaign_id>/daily", CampaignsStatsDailyView.as_view()),
    path("advertisers/<str:advertiser_id>/campaigns/daily", AdvertisersStatsDailyView.as_view()),
]