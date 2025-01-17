import csv
from django.core.management.base import BaseCommand, CommandError
from coverage.models import CoverageData
from django.db import transaction


class Command(BaseCommand):
    help = "Load network coverage data from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV file.")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                required_columns = {"Operateur", "x", "y", "2G", "3G", "4G"}

                # Validate header columns
                if not required_columns.issubset(reader.fieldnames):
                    missing = required_columns - set(reader.fieldnames)
                    self.stdout.write(self.style.ERROR(f"Missing expected column(s): {', '.join(missing)}"))
                    return

                records = []
                existing = set(CoverageData.objects.values_list('operator', 'x', 'y'))  # Preload existing records

                for row in reader:
                    key = (row["Operateur"], int(float(row["x"])), int(float(row["y"])))
                    if key in existing:
                        continue

                    records.append(
                        CoverageData(
                            operator=row["Operateur"],
                            x=int(float(row["x"])),
                            y=int(float(row["y"])),
                            g2=bool(int(row["2G"])),
                            g3=bool(int(row["3G"])),
                            g4=bool(int(row["4G"])),
                        )
                    )

                # Use a transaction for bulk creation
                with transaction.atomic():
                    CoverageData.objects.bulk_create(records, batch_size=1000)

                self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(records)} new records."))
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
