# instructors/views.py

from django.shortcuts import render, get_object_or_404
from courses.models import Course
from django.contrib.auth.decorators import login_required
from dsa_assignments.models import DSAAssignment
import requests

@login_required
def instructor_dashboard(request):
    # Fetch courses from Flask API
    FLASK_API_URL = "http://127.0.0.1:5001/api/courses"
    try:
        response = requests.get(FLASK_API_URL)
        response.raise_for_status()
        courses = response.json()
    except requests.exceptions.RequestException as e:
        courses = []
    return render(request, 'instructors/dashboard.html', {'courses': courses})


@login_required
def manage_assignments(request, course_id):
    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
        assignments = DSAAssignment.objects.filter(course=course)
        flask_course = None
    except Course.DoesNotExist:
        flask_api_url = f"http://127.0.0.1:5001/api/course/{course_id}"
        try:
            response = requests.get(flask_api_url)
            response.raise_for_status()
            flask_course = response.json()
            assignments = []
            course = None
        except requests.RequestException:
            flask_course = None
            assignments = []
            course = None
    return render(request, 'instructors/manage_assignments.html', {
        'course': course or flask_course,
        'assignments': assignments
    })