from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

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