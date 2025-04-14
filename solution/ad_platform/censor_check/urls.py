from django.urls import path

from .views import CensorStatusView, CensorWordsView

urlpatterns = [
    path("status", CensorStatusView.as_view()),
    path("words", CensorWordsView.as_view()),
]