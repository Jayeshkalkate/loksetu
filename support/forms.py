from django import forms

from .models import SupportTicket


class SupportTicketForm(forms.ModelForm):
    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()
        if len(subject) < 5:
            raise forms.ValidationError('Subject must be at least 5 characters long.')
        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 15:
            raise forms.ValidationError('Please describe the issue in at least 15 characters.')
        return message

    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
