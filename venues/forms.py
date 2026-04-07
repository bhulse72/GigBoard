from django import forms
from .models import Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = [
            'name',
            'description',
            'address',
            'city',
            'state',
            'capacity',
            'genre_tags',
            'website',
            'instagram',
            'profile_photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }