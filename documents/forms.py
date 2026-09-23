from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Document

ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif', 'txt']
MAX_FILE_SIZE = getattr(settings, 'DOCUMENT_MAX_SIZE', 10 * 1024 * 1024)  # 10MB default


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document title'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise ValidationError('No file selected.')

        # Check file size
        if file.size > MAX_FILE_SIZE:
            raise ValidationError(f'File size exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit.')

        # Check extension (additional to model validator)
        ext = file.name.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(f'Unsupported file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')

        return file

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Title is required.')
        return title