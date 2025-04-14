from django.db import models


class Advertiser(models.Model):
    advertiser_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Рекламодатель"
        verbose_name_plural = "Рекламодатели"


class MLScore(models.Model):
    client_id = models.ForeignKey("clients.Client", on_delete=models.CASCADE)
    advertiser_id = models.ForeignKey("advertisers.Advertiser", on_delete=models.CASCADE)
    score = models.IntegerField()
