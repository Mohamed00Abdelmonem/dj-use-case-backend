from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Seeds database with initial Use Case Hub data (delegates to seed_dummy_data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing portfolio data before seeding',
        )

    def handle(self, *args, **options):
        call_command('seed_dummy_data', *args, **options)
