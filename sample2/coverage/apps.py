import os
import logging
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command

# Configure the logger
logger = logging.getLogger(__name__)

class CoverageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coverage'

    def ready(self):
        # Connect post_migrate signal to load_data method
        post_migrate.connect(self.load_data, sender=self)

    def load_data(self, **kwargs):
        # Delay importing the model until the signal is triggered
        from .models import CoverageData

        # Check if data exists before loading
        if not CoverageData.objects.exists():
            csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'data.csv')
            if os.path.exists(csv_file_path):
                logger.info("No data found in the database. Loading data from CSV...")
                try:
                    call_command('load_csv', csv_file_path)
                    logger.info("Data loaded successfully.")
                except Exception as e:
                    logger.error(f"Failed to load data: {e}")
            else:
                logger.warning("CSV file not found. Skipping data load.")
        else:
            logger.info("Data already exists in the database. Skipping data load.")
