from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'rating', 'body']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title (15 words max)',
                'maxlength': '150',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.0',
                'max': '5.0',
                'step': '0.5',
                'placeholder': '0.0 – 5.0',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Write your review (250 words max)…',
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title.split()) > 15:
            raise forms.ValidationError('Title must be 15 words or fewer.')
        return title

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError('Rating is required.')
        if rating < 0 or rating > 5:
            raise forms.ValidationError('Rating must be between 0.0 and 5.0.')
        return rating

    def clean_body(self):
        body = self.cleaned_data.get('body', '').strip()
        if len(body.split()) > 250:
            raise forms.ValidationError('Review body must be 250 words or fewer.')
        return body
