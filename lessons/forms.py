from django import forms
from .models import LessonListing, TimeSlot


class LessonListingForm(forms.ModelForm):
    class Meta:
        model = LessonListing
        fields = ['title', 'description', 'style', 'price', 'duration_minutes', 'format', 'location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }