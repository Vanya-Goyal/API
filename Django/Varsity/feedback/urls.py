from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns=[
    path('submit/', views.submit_feedback, name='submit_feedback'),
    path('edit/<int:feedback_id>/', views.edit_feedback, name='edit_feedback'),
    path('', views.feedback_page, name='feedback'),
    path('update/<int:feedback_id>/', views.update_feedback, name='update_feedback'),
    path('delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback')
]