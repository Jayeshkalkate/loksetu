import re

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


def clean_indian_mobile(value):
    digits = re.sub(r'[\s\-]', '', value or '')
    digits = re.sub(r'^(\+91|0)', '', digits)
    if digits and not re.fullmatch(r'[6-9]\d{9}', digits):
        raise forms.ValidationError('Enter a valid 10-digit Indian mobile number.')
    return digits


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile', 'district')

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists. Try logging in or resetting your password.')
        return email

    def clean_mobile(self):
        return clean_indian_mobile(self.cleaned_data.get('mobile'))
