from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
     path('payment/', views.payment_page, name='payment'),
    path('confirm/', views.confirm_payment, name='confirm_payment'),
]
