import pytest

from clients.models import Client


@pytest.fixture
def client():
    return Client.objects.create(
        client_id="test_client_id",
        login="test_login",
        age=20,
        location="test_location",
        gender="MALE",
    )

