from django.urls import path
from . import views
app_name = 'assignments' 
urlpatterns = [
    path('course_list/', views.course_list, name='course_list'), 
    path('courses/<int:course_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_details'),
    path('assignment/<int:assignment_id>/result/', views.assignment_result, name='assignment_result'),
]