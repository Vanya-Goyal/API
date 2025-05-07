from django.db import models
from django.conf import settings
from courses.models import Course
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = get_user_model()

class DSAAssignment(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Easy')
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"

class DSAStudentSubmission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(DSAAssignment, on_delete=models.CASCADE)
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"