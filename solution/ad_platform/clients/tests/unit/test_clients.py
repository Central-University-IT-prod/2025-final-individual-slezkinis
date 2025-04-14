import pytest


@pytest.mark.django_db
def test_client(client):
    assert client.client_id == "test_client_id"
    assert client.login == "test_login"
    assert client.age == 20
    assert client.location == "test_location"
    assert client.gender == "MALE"


