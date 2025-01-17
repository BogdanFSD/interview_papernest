import requests
from pyproj import Transformer
from requests.exceptions import HTTPError

wgs84_to_lambert93_transformer = Transformer.from_crs(
    "EPSG:4326", "EPSG:2154", always_xy=True
)

def wgs84_to_lambert93(lon, lat):
    """
    Convert WGS84 (EPSG:4326) to Lambert-93 (EPSG:2154).
    Returns (x, y).
    """
    x, y = wgs84_to_lambert93_transformer.transform(lon, lat)
    return x, y

def get_coordinates(address):
    """
    Get WGS84 coordinates for a given address using an external geocoding API.
    """
    if not address or not isinstance(address, str) or len(address.strip()) == 0:
        raise ValueError("Invalid address provided. Address must be a non-empty string.")

    url = f"https://api-adresse.data.gouv.fr/search/?q={address}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            return data["features"][0]["geometry"]["coordinates"]
        return None
    except HTTPError:
        raise ValueError(f"Error fetching coordinates for address '{address}'")
    except Exception:
        raise ValueError(f"Unexpected error occurred while fetching coordinates for address '{address}'")