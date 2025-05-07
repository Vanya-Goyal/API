# instructors/urls.py

from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='dashboard'),
    path('course/<int:course_id>/assignments/manage/', views.manage_assignments, name='manage_assignments'),

]
