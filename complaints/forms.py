from django import forms
from django.utils import timezone

from .models import Complaint, validate_upload


class ComplaintForm(forms.ModelForm):
    evidence = forms.FileField(required=False, validators=[validate_upload], label='Photo, document or video',
                               help_text='JPG, PNG, PDF or MP4, up to 10 MB.')

    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'district', 'taluka', 'village_city', 'address',
                  'incident_date', 'latitude', 'longitude', 'additional_info']
        widgets = {'incident_date': forms.DateInput(attrs={'type': 'date'}),
                   'description': forms.Textarea(attrs={'rows': 4}),
                   'additional_info': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control form-control-lg')

    def clean_description(self):
        d = self.cleaned_data['description'].strip()
        if len(d) < 15:
            raise forms.ValidationError('Please describe the problem in a little more detail (at least 15 characters).')
        return d

    def clean_incident_date(self):
        d = self.cleaned_data['incident_date']
        if d > timezone.localdate():
            raise forms.ValidationError('The incident date cannot be in the future.')
        return d

    def clean(self):
        data = super().clean()
        if (data.get('latitude') is None) != (data.get('longitude') is None):
            raise forms.ValidationError('Provide both latitude and longitude, or neither.')
        return data
