import re
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Complaint


class ComplaintForm(forms.ModelForm):
    # Override fields for custom validation
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],
        widget=forms.TextInput(attrs={'placeholder': '10-digit mobile number'})
    )
    aadhaar = forms.CharField(
        max_length=12,
        required=False,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit Aadhaar number.')],
        widget=forms.TextInput(attrs={'placeholder': 'Optional 12-digit Aadhaar'})
    )
    pincode = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pincode.')],
        widget=forms.TextInput(attrs={'placeholder': '6-digit pincode'})
    )
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Complaint
        fields = [
            'full_name', 'phone', 'email', 'gender', 'aadhaar',
            'state', 'district', 'taluka', 'village', 'ward', 'pincode',
            'department', 'title', 'description', 'issue_location', 'issue_date',
            'evidence', 'latitude', 'longitude'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValidationError('Enter a valid email address.')
        return email


class TrackComplaintForm(forms.Form):
    complaint_id = forms.CharField(
        max_length=20,
        label='Complaint ID',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. LKS-MH-XXXXXX'})
    )