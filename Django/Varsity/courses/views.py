from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Course
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Course
from django.db.models import Q
from .forms import CourseForm 
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import Http404

def course_list(request):
    
    FLASK_API_URL = "http://127.0.0.1:5001/api/courses"
    try:
        response = requests.get(FLASK_API_URL)
        response.raise_for_status()
        flask_courses = response.json()
    except requests.exceptions.RequestException as e:
        flask_courses = []
        messages.error(request, f"Could not fetch courses from Flask API: {e}")

    
    query = request.GET.get('q', '').lower() if request.GET.get('q') else ''
    sort_by = request.GET.get('sort')
    category = request.GET.get('category', '').lower() if request.GET.get('category') else ''

    
    if query:
        flask_courses = [c for c in flask_courses if query in c.get('title', '').lower()]
    if category:
        flask_courses = [c for c in flask_courses if category == c.get('category', '').lower()]

    
    if sort_by == 'price_asc':
        flask_courses = sorted(flask_courses, key=lambda x: x.get('price', 0))
    elif sort_by == 'price_desc':
        flask_courses = sorted(flask_courses, key=lambda x: x.get('price', 0), reverse=True)

    
    paginator = Paginator(flask_courses, 6)
    page = request.GET.get('page')
    courses = paginator.get_page(page)

    
    categories = list(set(c.get('category', '') for c in flask_courses))

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        'sort_by': sort_by
    })

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})

@login_required
def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user not in course.students.all():
        course.students.add(request.user)
    return render(request, 'courses/payment_success.html', {'course': course})


def is_instructor(user):
    return user.is_authenticated or user.role == 'instructor'

#Instructor Dashboard View
@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    
    FLASK_API_URL = "http://127.0.0.1:5001/api/courses"
    try:
        response = requests.get(FLASK_API_URL)
        response.raise_for_status()
        courses = response.json()
    except requests.exceptions.RequestException as e:
        courses = []
        messages.error(request, f"Could not fetch courses from Flask API: {e}")
    return render(request, 'courses/instructor_dashboard.html', {'courses': courses})

# consuming api's

import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .forms import CourseForm
from .models import Course

FLASK_API_URL = "http://127.0.0.1:5001/api/courses"

@login_required
def add_course(request):
    
    if request.user.role != 'instructor' and not request.user.is_superuser:
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            
            course_data = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'price': float(form.cleaned_data['price']),
                'category': form.cleaned_data['category'],
                'instructor_id': request.user.id,
            }

            
            if 'image' in request.FILES:
                fs = FileSystemStorage()
                image = request.FILES['image']
                filename = fs.save(image.name, image)
                course_data['image_url'] = request.build_absolute_uri(fs.url(filename))

            try:
                
                response = requests.post(
                    FLASK_API_URL,
                    json=course_data,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()  

                
                course = Course(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    price=form.cleaned_data['price'],
                    category=form.cleaned_data['category'],
                    instructor=request.user,
                )

               
                if 'image' in request.FILES:
                    course.image_url = request.build_absolute_uri(fs.url(filename))

                course.save() 

                messages.success(request, "Course created successfully in both Flask and Django!")
                return redirect('courses:instructor_dashboard')

            except requests.exceptions.RequestException as e:
               
                if 'image_url' in course_data:
                    fs.delete(filename)
                error_msg = str(e)
                if hasattr(e, 'response') and e.response.text:
                    error_msg = e.response.json().get('error', error_msg)
                messages.error(request, f"API Error: {error_msg}")
    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})


@login_required
@user_passes_test(is_instructor)
def edit_course(request, course_id):
    flask_api_url = f"http://127.0.0.1:5001/api/course/{course_id}"
   
    if request.method == 'GET':
        try:
            response = requests.get(flask_api_url)
            response.raise_for_status()
            course_data = response.json()
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not fetch course from Flask API: {e}")
            return redirect('courses:instructor_dashboard')
        return render(request, 'courses/edit_course.html', {'course': course_data})
    
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price', 0)),
            'category': request.POST.get('category'),
        }
        try:
            put_response = requests.put(flask_api_url, json=data)
            put_response.raise_for_status()
           
            from .models import Course
            try:
                course = Course.objects.get(pk=course_id)
                course.title = data['title']
                course.description = data['description']
                course.price = data['price']
                course.category = data['category']
                course.save()
            except Course.DoesNotExist:
                pass 
            messages.success(request, "Course updated successfully in Flask! (Django updated if present)")
            return redirect('courses:instructor_dashboard')
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Failed to update course in Flask: {e}")
            return redirect('courses:instructor_dashboard')


@login_required
@user_passes_test(is_instructor)
def delete_course(request, course_id):
    flask_api_url = f"http://127.0.0.1:5001/api/course/{course_id}"
    
    if request.method == 'GET':
        try:
            response = requests.get(flask_api_url)
            response.raise_for_status()
            course_data = response.json()
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not fetch course from Flask API: {e}")
            return redirect('courses:instructor_dashboard')
        return render(request, 'courses/confirm_delete.html', {'course': course_data})
    
    if request.method == 'POST':
        flask_deleted = False
        django_deleted = False
        try:
            del_response = requests.delete(flask_api_url)
            del_response.raise_for_status()
            flask_deleted = True
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Failed to delete course from Flask: {e}")
        
        from .models import Course
        try:
            course = Course.objects.get(pk=course_id)
            course.delete()
            django_deleted = True
        except Course.DoesNotExist:
            pass  
        if flask_deleted:
            messages.success(request, "Course deleted successfully from Flask." + (" Also deleted from Django." if django_deleted else ""))
        return redirect('courses:instructor_dashboard')