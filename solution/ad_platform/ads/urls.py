from django.urls import path
from .views import AdsView, ClickView


urlpatterns = [
    path("", AdsView.as_view()),
    path("/<str:ad_id>/click", ClickView.as_view()),
]