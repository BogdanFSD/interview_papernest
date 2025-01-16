from app.utility import wgs84_to_lambert93, distance_lambert93


def test_wgs84_to_lambert93():
    lon, lat = 2.3522, 48.8566  # Coordinates for Paris
    x, y = wgs84_to_lambert93(lon, lat)
    assert isinstance(x, float), "x should be a float"
    assert isinstance(y, float), "y should be a float"


def test_distance_lambert93():
    x1, y1 = 102980, 6847973
    x2, y2 = 103113, 6848661
    distance = distance_lambert93(x1, y1, x2, y2)
    assert isinstance(distance, float), "Distance should be a float"
    assert distance > 0, "Distance should be greater than 0"
