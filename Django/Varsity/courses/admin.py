

# Register your models here.
from django.contrib import admin
from .models import Course

admin.site.register(Course)
class CourseAdmin(admin.ModelAdmin):
   # list_display = ('title', 'price', 'category', 'instructor')
    list_display = ('title', 'description', 'instructor', 'price', 'category')  # Example fields

    list_filter = ('category',)
    search_fields = ('title', 'description')