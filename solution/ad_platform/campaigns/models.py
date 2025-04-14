from django.db import models


GENDERS = (
    ("MALE", "male"),
    ("FEMALE", "female"),
    ("ALL", "all")
)
class Campaign(models.Model):
    campaign_id = models.CharField(max_length=100, primary_key=True)
    advertiser_id = models.ForeignKey("advertisers.Advertiser", on_delete=models.CASCADE, related_name="campaigns")
    impressions_limit = models.IntegerField()
    clicks_limit = models.IntegerField()
    cost_per_impression = models.FloatField()
    cost_per_click = models.FloatField()
    ad_title = models.CharField(max_length=100)
    ad_text = models.TextField()
    start_date = models.IntegerField()
    end_date = models.IntegerField()
    gender = models.CharField(max_length=1000, choices=GENDERS, blank=True, null=True)
    age_from = models.IntegerField(blank=True, null=True)
    age_to = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=1000, blank=True, null=True) 
    class Meta:
        verbose_name = "Рекламная кампания"
        verbose_name_plural = "Рекламные кампании"


class CampaignImage(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, related_name="images")
    image = models.ImageField()

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
