from django import forms
from .models import DSAAssignment
from .models import DSAStudentSubmission

class DSAAssignmentForm(forms.ModelForm):
    class Meta:
        model = DSAAssignment
        fields = ['title', 'description','difficulty', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
             'due_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }

class DSAStudentSubmissionForm(forms.ModelForm):
    class Meta:
        model = DSAStudentSubmission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={'rows': 15, 'class': 'form-control', 'placeholder': 'Write your code here...'}),
        }