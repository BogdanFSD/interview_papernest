from celery import shared_task
from django.core.management import call_command

@shared_task(bind=True)
def reload_data(self):
    """
    Celery task to reload network coverage data from CSV.
    """
    try:
        call_command('load_csv', 'data.csv')  # Replace 'data.csv' with your CSV path
        return "Data reloaded successfully."
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)  # Retry up to 3 times
        return f"Failed to reload data: {e}"
