# dsa_assignments/forms.py

from django import forms
from .models import DSAAssignment

class DSAAssignmentForm(forms.ModelForm):
    class Meta:
        model = DSAAssignment
        fields = ['title', 'description', 'difficulty']
        widgets = {
            'difficulty': forms.Select(choices=[
                ('Easy', 'Easy'), 
                ('Medium', 'Medium'), 
                ('Hard', 'Hard')
            ])
        }
