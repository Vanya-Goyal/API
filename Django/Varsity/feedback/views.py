from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from courses.models import Course
import requests

# The URL of your Flask backend
FLASK_API_URL = 'http://127.0.0.1:5001/feedback'

def feedback_page(request):
    # Call Flask API to get existing feedback
    try:
        response = requests.get(f'{FLASK_API_URL}/all')
        feedbacks = response.json().get('feedbacks', [])
    except requests.exceptions.RequestException as e:
        feedbacks = []

    # Get courses from your database (example)
    courses = Course.objects.all()

    return render(request, 'feedback/feedback.html', {'feedbacks': feedbacks, 'courses': courses})


def submit_feedback(request):
    if request.method == 'POST':
        # Ensure you have the logged-in user's ID
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'User not authenticated'}, status=401)
            
        feedback_data = {
            'course_id': int(request.POST.get('course_id')),
            'student_id': request.user.id,  # Add this line
            'rating': int(request.POST.get('rating')),
            'comment': request.POST.get('comment', ''),
        }

        try:
            response = requests.post(f'{FLASK_API_URL}/add', json=feedback_data)
            return JsonResponse({'message': 'Feedback submitted successfully'}, status=200)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'message': 'Error while submitting feedback'}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=400)


def edit_feedback(request, feedback_id):
    # Fetch feedback from the Flask API to be edited
    try:
        response = requests.get(f'{FLASK_API_URL}/{feedback_id}')
        feedback = response.json().get('feedback', {})
    except requests.exceptions.RequestException as e:
        feedback = {}

    # Get courses from your database (example)
    courses = Course.objects.all()

    return render(request, 'feedback/edit_feedback.html', {'feedback': feedback, 'courses': courses})


def update_feedback(request, feedback_id):
    if request.method == 'POST':
        # Get updated feedback data from the form
        updated_feedback = {
            'course_id': request.POST.get('course_id'),
            'rating': request.POST.get('rating'),
            'comment': request.POST.get('comment'),
        }

        # Send the updated feedback to Flask API for updating
        try:
            response = requests.put(f'{FLASK_API_URL}/update/{feedback_id}', json=updated_feedback)
            return JsonResponse({'message': 'Feedback updated successfully'}, status=200)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'message': 'Error while updating feedback'}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

def delete_feedback(request, feedback_id):
    try:
        response = requests.delete(f'{FLASK_API_URL}/delete/{feedback_id}')
        return JsonResponse({'message': 'Feedback deleted successfully'}, status=200)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'message': 'Error while deleting feedback'}, status=500)

