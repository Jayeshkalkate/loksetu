from django import forms

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['department', 'purpose', 'preferred_date', 'preferred_time', 'notes']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_preferred_date(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        date = self.cleaned_data['preferred_date']
        if date < timezone.localdate():
            raise ValidationError('Preferred date cannot be in the past.')
        return date
