from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.files.uploadedfile import SimpleUploadedFile
from django.apps import apps
from django.views.generic import ListView, DetailView, CreateView


import requests

from img.forms import *
from img.models import *

@require_POST
@login_required
def upload_image(request):
     model_name = request.POST.get('model')
     object_id = request.POST.get('object_id')
     new_image = ImageForm().self_processing(request, model_name, object_id)
     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ImageListView(ListView):
    def get_active_image(self):
        img_id = int(self.kwargs.get('img_id'))
        image = get_object_or_404(Image, id=img_id)
        return image

    def get_core_object(self):
        active_image = self.get_active_image()
        core_object = active_image.content_object
        return core_object

    def get_queryset(self, *args, **kwargs):
        core_object = self.get_core_object()
        qs = core_object.images.exclude(id = int(self.kwargs.get('img_id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({'active_image': self.get_active_image(), 'core_object': self.get_core_object()})
        return context
