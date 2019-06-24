from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import AdvUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Адрес электронной почты', required=True)

    class Meta(UserCreationForm.Meta):
        model = AdvUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        user.send_confirmation_email()
        if commit:
            user.save()
        return user
