import pytest

from campaigns.models import Campaign

from advertisers.models import Advertiser


@pytest.fixture
def campaign():
    advertiser = Advertiser.objects.create(advertiser_id="e6b8e6a1-c8e5-4ebe-b634-dd976f4afdf7", name="string")
    return Campaign.objects.create(campaign_id="e6b8e6a1-c8e5-4ebe-b634-dd976f4afdf7", impressions_limit=0, clicks_limit=0, cost_per_impression=0, cost_per_click=0, ad_title="string", ad_text="string", start_date=0, end_date=0, gender="MALE", age_from=0, age_to=0, location="string", advertiser_id=advertiser)