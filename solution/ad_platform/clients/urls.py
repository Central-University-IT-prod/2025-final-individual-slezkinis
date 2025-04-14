from django.urls import path
from .views import ClientView, ClientsCreateView


urlpatterns = [
    path("bulk", ClientsCreateView.as_view()),
    path("<str:client_id>", ClientView.as_view()),
]