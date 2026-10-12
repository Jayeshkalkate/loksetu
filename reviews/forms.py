from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    def clean_comment(self):
        comment = self.cleaned_data['comment'].strip()
        if len(comment) < 10:
            raise forms.ValidationError('Please write at least 10 characters so your feedback is useful.')
        return comment

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} star{"s" if i != 1 else ""}') for i in range(5, 0, -1)],
                                    attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                              'placeholder': 'Share your experience with LOKSETU'}),
        }
