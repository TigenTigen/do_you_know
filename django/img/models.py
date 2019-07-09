from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from easy_thumbnails.fields import ThumbnailerImageField
from datetime import datetime

AUTH_USER_MODEL = get_user_model()

def get_timestamp_path(img, filename):
    timestamp = datetime.now().timestamp()
    return 'uploaded_images/{}'.format(timestamp)

class ImageManager(models.Manager):
    def check_images(self):
        qs = self.get_queryset()
        no_image_file_qs = qs.filter(image=None)
        no_image_file_qs.delete()

class Image(models.Model):
    is_cover = models.BooleanField('Обложка', default=False)
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Файл изображения')
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Тип связанного объекта')
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_images', null=True, blank=True, verbose_name='Пользователь')
    uploaded = models.DateTimeField('Дата и время загрузки изображения', auto_now_add=True)

    objects = ImageManager()

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['content_type', 'object_id', '-uploaded',]

    def __str__(self):
        return '{}'.format(self.id)

    def clean(self):
        if self.is_cover:
            object = self.content_object
            cover_images = object.images.filter(is_cover=True).distinct()
            if cover_images.exists():
                raise ValidationError('Для данного объекта уже назначено изображение-обложка')

    def get_absolute_url(self):
        return '/img/list/{}/'.format(self.id)
