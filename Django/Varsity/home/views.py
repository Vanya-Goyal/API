

# Create your views here.
from django.shortcuts import render

def homepage(request):
    return render(request, 'home/home.html')
# from django.urls import reverse

# def homepage(request):
#     course_url = reverse('courses:course_list')  # ✅ namespace included
#     return redirect(course_url)