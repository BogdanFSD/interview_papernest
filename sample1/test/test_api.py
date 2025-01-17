import pytest
from sample1.app import create_app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def client():
    app = create_app("app_config.TestingConfig")
    with app.test_client() as client:
        yield client


def test_api_no_address(client):
    response = client.get("/api/")
    assert response.status_code == 400
    assert response.json["message"] == "No address provided."


def test_api_invalid_address(client, requests_mock):
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search/?q=invalid_address",
        json={"features": []},  # Mocked response for no results
    )
    response = client.get("/api/?q=invalid_address")
    assert response.status_code == 404
    assert response.json["message"] == "Unable to fetch coordinates."


def test_api_valid_address(client, requests_mock):
    requests_mock.get(
        "https://api-adresse.data.gouv.fr/search/?q=42+rue+papernest+75011+Paris",
        json={
            "features": [
                {"geometry": {"coordinates": [2.3522, 48.8566]}}  # Mocked response
            ]
        },
    )
    response = client.get("/api/?q=42+rue+papernest+75011+Paris")
    assert response.status_code == 200
    assert "Orange" in response.json, "Orange operator missing in response"
