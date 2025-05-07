from django.core.management.base import BaseCommand
from courses.models import Course
import requests

class Command(BaseCommand):
    help = 'Sync courses from Flask API to Django DB'

    def handle(self, *args, **kwargs):
        response = requests.get('http://127.0.0.1:5001/api/courses')
        if response.status_code == 200:
            courses = response.json()
            for c in courses:
                course, created = Course.objects.update_or_create(
                    id=c['id'],
                    defaults={
                        'title': c['title'],
                        'description': c['description'],
                        'price': c['price'],
                        'category': c['category'],
                        # Add other fields as needed
                    }
                )
            self.stdout.write(self.style.SUCCESS('Courses synced successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch courses from Flask API'))