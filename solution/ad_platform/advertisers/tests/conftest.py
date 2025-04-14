import pytest

from advertisers.models import Advertiser


@pytest.fixture
def advertiser():
    return Advertiser.objects.create(advertiser_id="3fa85f64-5717-4562-b3fc-2c963f66afa6", name="string")