from django import forms
from img.models import Image
from django.contrib.auth import get_user_model

AUTH_USER_MODEL = get_user_model()

class ImageForm(forms.ModelForm):
    url = forms.URLField(required=False, label='или url-адресс изображения в Интернете')
    image = forms.ImageField(required=False, label=' Укажите путь к файлу на вашем компьютере')

    class Meta:
        model = Image
        fields = ['image', 'url',]
