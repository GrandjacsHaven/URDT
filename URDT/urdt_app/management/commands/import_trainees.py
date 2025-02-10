import os
from django.core.management.base import BaseCommand
from urdt_app.utils import import_trainees_from_csv

class Command(BaseCommand):
    help = 'Import trainees from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The full path to the CSV file.')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR("File not found: {}".format(csv_file)))
            return
        with open(csv_file, 'rb') as f:
            imported_count, skipped_count = import_trainees_from_csv(f)
        self.stdout.write(self.style.SUCCESS(
            f"Imported {imported_count} trainees. Skipped {skipped_count} duplicates."
        ))
