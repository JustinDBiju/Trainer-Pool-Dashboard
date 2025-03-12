from django import forms
from .models import TrainerData, Trainer

class TrainerDataForm(forms.ModelForm):
    class Meta:
        model = TrainerData
        fields = [
            'achievements', 'classes_scheduled', 'classes_taken', 
            'workshops', 'students_participated', 'students_won', 
            'course_referrals'
        ]
        widgets = {
            'achievements': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'classes_scheduled': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'classes_taken': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'workshops': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'students_participated': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'students_won': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'course_referrals': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['email', 'phone_number', 'designation', 'experience']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter designation'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Years of experience'}),
        }
