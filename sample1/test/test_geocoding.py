import requests_mock
from sample1.utility import address_to_coordinates


def test_address_to_coordinates():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api-adresse.data.gouv.fr/search/?q=42+rue+papernest+75011+Paris",
            json={
                "features": [
                    {"geometry": {"coordinates": [2.3522, 48.8566]}}  # Mocked response
                ]
            },
        )
        result = address_to_coordinates("42 rue papernest 75011 Paris")
        assert result == {"lon": 2.3522, "lat": 48.8566}, "Geocoding failed"
