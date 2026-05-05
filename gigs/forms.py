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
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'preferred_style': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }