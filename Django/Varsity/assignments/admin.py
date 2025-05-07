from django.contrib import admin
from .models import Assignment, Question, Option  # No Course here

class OptionInline(admin.TabularInline):
    model = Option
    extra = 2

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')  # updated for correct Course model
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'assignment')
    list_filter = ('assignment__course',)
    search_fields = ('text', 'assignment__title')
    inlines = [OptionInline]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text', 'question__text')
