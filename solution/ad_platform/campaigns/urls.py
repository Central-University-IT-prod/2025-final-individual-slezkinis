from django.urls import path

from .views import CampaignsView, CampaignGenerateTextView, CampaignView, CampaignImagesView, ImageView

urlpatterns = [
    path("", CampaignsView.as_view()),
    path('/generate_text', CampaignGenerateTextView.as_view()),
    path("/<str:campaign_id>", CampaignView.as_view()),
    path("/<str:campaign_id>/images", CampaignImagesView.as_view()),
    path("/<str:campaign_id>/images/<str:image_id>", ImageView.as_view()),
]