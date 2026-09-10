import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.portfolio.views import PortfolioImportView
from rest_framework.test import APIRequestFactory

class Command(BaseCommand):
    help = 'Seeds database with initial Use Case Hub data'

    def handle(self, *args, **options):
        current = Path(__file__).resolve()
        json_path = None
        for p in [current] + list(current.parents):
            candidate = p / 'use-case-hub-frontend' / 'public' / 'data' / 'use-case-hub.json'
            if candidate.exists():
                json_path = candidate
                break

        if not json_path or not json_path.exists():
            self.stdout.write(self.style.ERROR("Seed JSON file not found!"))
            return

        self.stdout.write(f"Reading seed data from {json_path}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        factory = APIRequestFactory()
        request = factory.post('/api/portfolio/import/', data, format='json')
        view = PortfolioImportView.as_view()
        response = view(request)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("Successfully seeded database from use-case-hub.json!"))
        else:
            self.stdout.write(self.style.ERROR(f"Seeding failed with status {response.status_code}: {response.data}"))
