# cart/models.py
from django.db import models
from django.conf import settings
from courses.models import Course
from django.utils import timezone

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    
    def total_price(self):
        return sum(course.price for course in self.courses.all())




class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} purchased {self.course.title}"
