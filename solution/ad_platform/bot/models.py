from django.db import models

from advertisers.models import Advertiser

class TgUser(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    adververtiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, null=True)
    

