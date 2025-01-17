import requests
import psycopg2
import logging
from math import sqrt
from flask import Flask
from pyproj import Transformer
from dotenv import load_dotenv
from app_config import Config

load_dotenv()


app = Flask(__name__)

wgs84_to_lambert93_transformer = Transformer.from_crs(
    "EPSG:4326", "EPSG:2154", always_xy=True
)


def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            dbname=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection failed: {e}")
        raise


def wgs84_to_lambert93(lon, lat):
    """
    Convert WGS84 (EPSG:4326) to Lambert-93 (EPSG:2154).
    Returns (x, y).
    """
    x, y = wgs84_to_lambert93_transformer.transform(lon, lat)
    return x, y


def distance_lambert93(x1, y1, x2, y2):
    """
    Calculate the Euclidean distance in Lambert-93.
    """
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def address_to_coordinates(address):
    """
    Fetch coordinates from an address using the French government's geocoding API.
    """
    url = f"https://api-adresse.data.gouv.fr/search/?q={address}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            coordinates = data["features"][0]["geometry"]["coordinates"]
            return {"lon": coordinates[0], "lat": coordinates[1]}
        else:
            logging.warning(f"No features found for address: {address}")
    except requests.RequestException as e:
        logging.error(f"Error fetching coordinates for address '{address}': {e}")
    return None

