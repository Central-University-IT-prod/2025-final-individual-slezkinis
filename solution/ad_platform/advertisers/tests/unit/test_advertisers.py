import pytest

@pytest.mark.django_db
def test_advertiser_create(advertiser):
    assert advertiser.advertiser_id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert advertiser.name == "string"