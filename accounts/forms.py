from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile', 'district')

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.fields['email'].required = True
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control')
