from django import forms
from .models import GigListing


class GigListingForm(forms.ModelForm):
    class Meta:
        model = GigListing
        fields = [
            'title',
            'location',
            'event_date',
            'start_time',
            'pay',
            'preferred_style',
            'description',
            'is_open',
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }