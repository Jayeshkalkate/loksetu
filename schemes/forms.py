import json
from django import forms
from django.core.exceptions import ValidationError
from .models import Scheme


class SchemeForm(forms.ModelForm):
    class Meta:
        model = Scheme
        fields = [
            'title', 'description', 'eligibility', 'benefits',
            'category', 'level', 'state', 'district', 'taluka',
            'village', 'official_link', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'eligibility': forms.Textarea(attrs={'rows': 3}),
            'benefits': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Title is required.")
        return title


class BulkUploadForm(forms.Form):
    file = forms.FileField(label='Select JSON file')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError("No file selected.")
        if not file.name.endswith('.json'):
            raise ValidationError("Only JSON files are allowed.")
        return file


class SchemeSearchForm(forms.Form):
    search = forms.CharField(required=False, max_length=100)
    category = forms.ChoiceField(choices=[('', 'All')] + Scheme.CATEGORY_CHOICES, required=False)
    level = forms.ChoiceField(choices=[('', 'All')] + Scheme.LEVEL_CHOICES, required=False)