import pytest


@pytest.mark.django_db
def test_campaign(campaign):
    '''
    {
  "impressions_limit": 0,
  "clicks_limit": 0,
  "cost_per_impression": 0,
  "cost_per_click": 0,
  "ad_title": "string",
  "ad_text": "string",
  "start_date": 0,
  "end_date": 0,
  "targeting": {
    "gender": "MALE",
    "age_from": 0,
    "age_to": 0,
    "location": "string"
  }
}'''
    assert campaign.campaign_id == "e6b8e6a1-c8e5-4ebe-b634-dd976f4afdf7"
    assert campaign.impressions_limit == 0
    assert campaign.clicks_limit == 0
    assert campaign.cost_per_impression == 0
    assert campaign.cost_per_click == 0
    assert campaign.ad_title == "string"
    assert campaign.ad_text == "string"
    assert campaign.start_date == 0
    assert campaign.end_date == 0
    assert campaign.gender == "MALE"
    assert campaign.age_from == 0
    assert campaign.age_to == 0
    assert campaign.location == "string"
    assert campaign.advertiser_id.advertiser_id == "e6b8e6a1-c8e5-4ebe-b634-dd976f4afdf7"
    
