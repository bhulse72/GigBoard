from django import forms
from .models import User

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'bio',
            'location',
            'stage_name',
            'music_style',
            'interests',
            'soundcloud_url',
            'instagram_url',
            'spotify_url',
        ]