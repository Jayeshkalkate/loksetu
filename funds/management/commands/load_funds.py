import json
from django.core.management.base import BaseCommand
from funds.models import Fund, Location

class Command(BaseCommand):
    help = 'Load funds data from JSON'

    def handle(self, *args, **kwargs):
        with open('funds/data/funds.json') as f:
            data = json.load(f)

        for item in data:
            location, _ = Location.objects.get_or_create(
                name=item['location'],
                type='district'
            )

            Fund.objects.create(
                title=item['title'],
                department=item['department'],
                total_amount=item['total_amount'],
                released_amount=item['released_amount'],
                location=location,
                year=item['year']
            )

        self.stdout.write(self.style.SUCCESS('Data Loaded Successfully'))
        
