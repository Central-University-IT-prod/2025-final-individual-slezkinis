from django.urls import path

from .views import ClickImmersiveView, ClickImmersiveDailyView, CostImmersiveClicksDailyView, TotalProfitView, TotalConversationView
urlpatterns = [
    path("clicks_immersive", ClickImmersiveView.as_view()),
    path("clicks_immersive/daily", ClickImmersiveDailyView.as_view()),
    path("cost_immersive_clicks/daily", CostImmersiveClicksDailyView.as_view()),
    path("total_profit", TotalProfitView.as_view()),
    path("total-conversation", TotalConversationView.as_view()),
]