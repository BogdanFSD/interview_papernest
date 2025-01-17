import os
import json
from django.test import TestCase, Client
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch
from .models import CoverageData
from .utils import wgs84_to_lambert93, get_coordinates


class CoverageDataModelTest(TestCase):
    def test_coverage_data_creation(self):
        """Test creating a CoverageData record."""
        coverage = CoverageData.objects.create(
            operator="20801",
            x=102980,
            y=6847973,
            g2=True,
            g3=True,
            g4=False,
        )
        self.assertEqual(coverage.operator, "20801")
        self.assertTrue(coverage.g2)
        self.assertFalse(coverage.g4)


class GetNetworkCoverageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        CoverageData.objects.create(
            operator="20801",
            x=102980,
            y=6847973,
            g2=True,
            g3=True,
            g4=False,
        )

    @patch("coverage.utils.get_coordinates")
    def test_get_network_coverage_success(self, mock_get_coordinates):
        """Test successful network coverage lookup."""
        mock_get_coordinates.return_value = (2.0, 48.0)
        response = self.client.get("/api/", {"q": "Paris"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("Orange", data)

    def test_get_network_coverage_no_address(self):
        """Test network coverage lookup with no address provided."""
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "No address provided")


class LoadCSVCommandTest(TestCase):
    def setUp(self):
        self.csv_file_path = os.path.join(os.path.dirname(__file__), "test_data.csv")
        with open(self.csv_file_path, "w") as f:
            f.write("Operateur;x;y;2G;3G;4G\n20801;102980;6847973;1;1;0\n")

    def tearDown(self):
        os.remove(self.csv_file_path)

    def test_load_csv_success(self):
        """Test the load_csv management command."""
        call_command("load_csv", self.csv_file_path)
        self.assertEqual(CoverageData.objects.count(), 77148 )

    def test_load_csv_file_not_found(self):
        """Test load_csv with a non-existent file."""
        with self.assertRaises(CommandError):
            call_command("load_csv", "non_existent.csv")


class UtilsTest(TestCase):
    def test_wgs84_to_lambert93(self):
        """Test WGS84 to Lambert93 coordinate conversion."""
        x, y = wgs84_to_lambert93(2.0, 48.0)
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)

    @patch("coverage.utils.requests.get")
    def test_get_coordinates_success(self, mock_get):
        """Test successful geocoding."""
        mock_get.return_value.json.return_value = {
            "features": [{"geometry": {"coordinates": [2.0, 48.0]}}]
        }
        coordinates = get_coordinates("Paris")
        self.assertEqual(coordinates, [2.0, 48.0])

    @patch("coverage.utils.requests.get")
    def test_get_coordinates_failure(self, mock_get):
        """Test geocoding failure."""
        mock_get.return_value.json.return_value = {"features": []}
        coordinates = get_coordinates("Invalid Address")
        self.assertIsNone(coordinates)
