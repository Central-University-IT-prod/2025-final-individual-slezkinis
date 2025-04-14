from django.contrib import admin

from .models import Campaign, CampaignImage

admin.site.register(Campaign)
admin.site.register(CampaignImage)