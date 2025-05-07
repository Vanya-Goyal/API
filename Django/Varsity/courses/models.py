from django.db import models
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  related_name='instructor_courses', null=True)
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    def __str__(self):
        return self.title



class CoursePurchase(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    purchased_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"