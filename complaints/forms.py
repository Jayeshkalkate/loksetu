from django import forms
from .models import Complaint, validate_upload


class ComplaintForm(forms.ModelForm):
    evidence = forms.FileField(required=False, validators=[validate_upload], label='Photo, document or video')

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
