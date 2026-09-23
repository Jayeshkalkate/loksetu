from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Citizen


class CustomAuthenticationForm(AuthenticationForm):
    """Login form with additional validation."""
    username = forms.CharField(label="Phone Number", max_length=10)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomUserCreationForm(UserCreationForm):
    """Registration form with citizen fields."""
    full_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],
        required=True,
    )
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    aadhaar = forms.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit Aadhaar number.')],
        required=False,
    )
    district = forms.CharField(max_length=100, required=True)
    taluka = forms.CharField(max_length=100, required=True)
    village = forms.CharField(max_length=100, required=True)
    ward = forms.CharField(max_length=20, required=True)
    pincode = forms.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pincode.')],
        required=True,
    )
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = (
            "full_name",
            "phone_number",
            "email",
            "password1",
            "password2",
            "gender",
            "aadhaar",
            "district",
            "taluka",
            "village",
            "ward",
            "pincode",
            "address",
        )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if User.objects.filter(username=phone).exists():
            raise ValidationError("This phone number is already registered.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["phone_number"]
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
        return user


class CitizenProfileForm(forms.ModelForm):
    """Form for editing citizen profile."""
    full_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],
        required=True,
    )

    class Meta:
        model = Citizen
        fields = (
            "gender",
            "aadhaar",
            "district",
            "taluka",
            "village",
            "ward",
            "pincode",
            "address",
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["full_name"].initial = self.instance.user.first_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["phone_number"].initial = self.instance.phone

    def save(self, commit=True):
        citizen = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data["full_name"]
            self.user.email = self.cleaned_data["email"]
            if commit:
                self.user.save()
        citizen.phone = self.cleaned_data["phone_number"]
        if commit:
            citizen.save()
        return citizen