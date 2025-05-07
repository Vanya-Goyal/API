from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart
from courses.models import Course
from django.contrib.auth.decorators import login_required
from .models import Purchase
# @login_required
# def add_to_cart(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart.courses.add(course)
#     return redirect('courses:course_list')
@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add the course to the cart if it's not already there
    if course not in cart.courses.all():
        cart.courses.add(course)

    # Redirect to the cart detail page after adding
    return redirect('cart:view_cart')  # 👈 Make sure this URL name matches your cart detail URL pattern


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    courses = cart.courses.all()
    total = cart.total_price()
    return render(request, 'cart/view_cart.html', {
        'courses': courses,
        'total': total
    })

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)  # ✅ fixed here
    cart.courses.clear()  # simulate purchase
    return render(request, 'cart/checkout_success.html')

@login_required
def payment_page(request):
    cart = Cart.objects.get(user=request.user)  # ✅ fixed here
    return render(request, 'cart/payment.html', {'cart': cart})

@login_required
def confirm_payment(request):
    cart = Cart.objects.get(user=request.user)

    for course in cart.courses.all():
        course.students.add(request.user)  # enroll student
        Purchase.objects.get_or_create(user=request.user, course=course)  # 🔥 record history

    cart.courses.clear()  # empty cart
    return redirect('accounts:student_dashboard')