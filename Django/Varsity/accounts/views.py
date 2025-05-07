from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from courses.models import Course
from .models import CustomUser
import requests

# api_forsignup='http://127.0.0.1:5000/signup'
# api_forlogin='http://127.0.0.1:5000/login'
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')

            if role == 'instructor':
                user.is_staff = True
            user.save()

            
            return redirect('accounts:login')  

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

# def signup_view(request):
#     if request.method == "POST":
#         name = request.POST['name']
#         email = request.POST['email']
#         password = request.POST['password']
#         mobile = request.POST.get('mobile', '')

#         response = requests.post(api_forsignup, json={
#             "name": name,
#             "email": email,
#             "password": password,
#             "mobile": mobile
#         })

#         data = response.json()
#         if response.status_code == 201:
#             return redirect("login_view")  # Registration successful
#         else:
#             return render(request, "signup.html", {"error": data.get('error', 'Registration failed')})
    
#     return render(request, "signup.html")                                                                                                                                                                                                    

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('accounts:student_dashboard') 
            elif user.role == 'instructor':
                return redirect('instructors:dashboard')  
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')

# def login_view(request):
#     if request.method == "POST":
#         email = request.POST['email']
#         password = request.POST['password']
        
#         response = requests.post(api_forlogin, json={
#             "email": email,
#             "password": password
#         })
        
#         data = response.json()
#         if response.status_code == 200:
#             request.session['user'] = data['user']  # Store user in Django session
#             return redirect('dashboard')  # your Django route
#         else:
#             return render(request, "login.html", {"error": data.get('error', 'Login failed')})
    
#     return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

# def signup_view(request):
#     if request.method == 'POST':
#         fullname = request.POST.get('fullname')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
#         mobile = request.POST.get('mobile')

#         # Send data to Flask signup API
#         response = requests.post(api_forsignup, data={
#             'fullname': fullname,
#             'email': email,
#             'password': password,
#             'confirm_password': confirm_password,
#             'mobile': mobile,
#         })

#         # Check Flask API response
#         if 'success' in response.text.lower():
#             messages.success(request, 'Signup successful! Please log in.')
#             return redirect('accounts:login')
#         else:
#             messages.error(request, 'Signup failed: ' + response.text)
#             return redirect('accounts:signup')

#     return render(request, 'accounts/signup.html')

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         response = requests.post(api_forlogin, data={
#             'email': email,
#             'password': password,
#         })

#         # Assuming Flask returns plain text or JSON like {"status": "success", "role": "student"}
#         try:
#             result = response.json()
#             if result.get('status') == 'success':
#                 role = result.get('role')

#                 # Optional: manually set a session or token here if needed
#                 request.session['email'] = email
#                 request.session['role'] = role

#                 if role == 'student':
#                     return redirect('accounts:student_dashboard')
#                 elif role == 'instructor':
#                     return redirect('instructors:dashboard')
#                 else:
#                     return redirect('dashboard')
#             else:
#                 messages.error(request, 'Invalid credentials.')
#         except Exception as e:
#             messages.error(request, 'Login failed or server error.')

#     return render(request, 'accounts/login.html')


@login_required
def student_dashboard(request):
    enrolled_courses = Course.objects.filter(students=request.user)
    return render(request, 'accounts/student_dashboard.html', {
        'enrolled_courses': enrolled_courses
    })
@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'instructors/dashboard.html')

