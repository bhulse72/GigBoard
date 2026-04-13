from django import forms
from .models import CollaborationRequest


class CollaborationRequestForm(forms.ModelForm):
    class Meta:
        model = CollaborationRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }