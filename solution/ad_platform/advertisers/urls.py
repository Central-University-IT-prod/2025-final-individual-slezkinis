from django.urls import path, include

from .views import AdvertisersGetView, AdvertisersCreateView


urlpatterns = [
    path("<str:advertiser_id>/campaigns", include("campaigns.urls")),
    path("bulk", AdvertisersCreateView.as_view()),
    path("<str:advertiser_id>", AdvertisersGetView.as_view()),
]