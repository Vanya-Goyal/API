from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),  
    path('<int:course_id>/buy/', views.buy_course, name='buy_course'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('instructor/courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('instructor/courses/add/', views.add_course, name='add_course'),  # instead of create_course
   

]
