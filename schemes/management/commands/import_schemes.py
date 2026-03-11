from django.core.management.base import BaseCommand
from schemes.models import Scheme
import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):

    help = "Import government schemes from india.gov.in"

    def handle(self, *args, **kwargs):

        url = "https://www.india.gov.in/my-government/schemes"

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException:
            self.stdout.write(self.style.ERROR("Failed to connect to website"))
            return

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR("Website returned error"))
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # find links inside scheme list
        links = soup.select("ul li a")

        count = 0

        for link in links:

            title = link.text.strip()

            # skip empty or short titles
            if len(title) < 5:
                continue

            # avoid UI words
            skip_words = ["Search", "Toggle", "Text Size", "Contrast"]

            if any(word in title for word in skip_words):
                continue

            obj, created = Scheme.objects.get_or_create(
                title=title,
                scheme_level="central",
                defaults={
                    "description": "Imported automatically from india.gov.in",
                    "eligibility": "Check official government website",
                    "benefits": "Varies depending on scheme",
                    "category": "Government Scheme",
                    "source": "india.gov.in",
                    "official_link": url,
                    "is_verified": True
                }
            )

            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} schemes imported successfully"))