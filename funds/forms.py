from django import forms
from django.core.exceptions import ValidationError
from .models import Fund, Project, Location


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ['title', 'department', 'total_amount', 'released_amount', 'location', 'year']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_amount')
        released = cleaned_data.get('released_amount')
        if total is not None and released is not None and released > total:
            raise ValidationError("Released amount cannot exceed total amount.")
        return cleaned_data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['fund', 'name', 'sanctioned_amount', 'used_amount', 'status', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        used = cleaned_data.get('used_amount')
        sanctioned = cleaned_data.get('sanctioned_amount')
        if sanctioned is not None and used is not None and used > sanctioned:
            raise ValidationError("Used amount cannot exceed sanctioned amount.")
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise ValidationError("End date cannot be before start date.")
        return cleaned_data


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'type', 'parent']