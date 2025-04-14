from django.db import models
from campaigns.models import Campaign
from clients.models import Client

class View(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="views")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="views")
    date = models.IntegerField()
    price = models.FloatField()

    class Meta:
        unique_together = ("campaign", "client")


class Click(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="clicks")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="clicks")
    date = models.IntegerField()
    price = models.FloatField()

    class Meta:
        unique_together = ("campaign", "client")
