from django.urls import path
from . import views

app_name = 'dsa_assignments'

urlpatterns = [
    #path('instructor/list/', views.assignment_list, name='assignment_list'),
    path('instructor/course/<int:course_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('instructor/course/<int:course_id>/add/', views.add_assignment, name='add_assignment'),
    path('instructor/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('instructor/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
]
# Student Side
urlpatterns += [
    path('course/<int:course_id>/assignments/', views.assignment_list_student, name='assignment_list_student'),
    path('course/<int:course_id>/assignment/<int:assignment_id>/', views.assignment_detail_student, name='assignment_detail_student'),
    path('assignment/<int:assignment_id>/submit/', views.create_submission, name='create_submission'),
    path('course/<int:course_id>/assignment/<int:assignment_id>/submissions/', views.student_submissions, name='student_submissions'),
    path('submission/<int:submission_id>/edit/', views.edit_submission, name='edit_submission'),
    path('submission/<int:submission_id>/delete/', views.delete_submission, name='delete_submission'),
]
