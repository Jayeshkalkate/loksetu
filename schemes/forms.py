
from django import forms
from .models import Scheme

class BulkUploadForm(forms.Form):
    file = forms.FileField()

class SchemeForm(forms.ModelForm):
    class Meta:
        model = Scheme
        fields = [
            'title',
            'description',
            'eligibility',
            'benefits',
            'category',
            'level',
            'state',
            'district',
            'taluka',
            'village',
            'official_link',
            'image'
        ]