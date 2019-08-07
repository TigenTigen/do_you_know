from django import forms
from django.apps import apps
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
import requests

from img.models import Image

class ImageForm(forms.ModelForm):
    url = forms.URLField(required=False, label='или url-адресс изображения в Интернете')
    image = forms.ImageField(required=False, label=' Укажите путь к файлу на вашем компьютере')

    class Meta:
        model = Image
        fields = ['image', 'url',]

    def self_processing(self, request, model_name, object_id):
        model = apps.get_model(app_label='core', model_name=model_name, require_ready=True)
        object = get_object_or_404(model, pk=object_id)
        url = request.POST.get('url')
        if url and url != '':
            r = requests.get(url)
            file_data = {'image': SimpleUploadedFile('temp_image.jpg', r.content)}
            image_form = ImageForm(request.POST, file_data)
        else:
            image_form = ImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            new_image = image_form.save()
            new_image.content_object = object
            new_image.user = request.user
            new_image.save()
            return new_image
        return None

    def cover_processing(self, request, model_name, object_id):
        new_image = ImageForm().self_processing(request, model_name, object_id)
        if new_image:
            new_image.is_cover = True
            new_image.save()

    def demo_download_processing(self, object, url, user):
        r = requests.get(url)
        if r.status_code == 200:
            file_data = {'image': SimpleUploadedFile('temp_image.jpg', r.content)}
            image_form = ImageForm({'url': url}, file_data)
            if image_form.is_valid():
                new_image = image_form.save()
                new_image.content_object = object
                new_image.user = user
                new_image.is_cover = True
                new_image.save()
