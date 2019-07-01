from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.contrib.auth import get_user_model
from easy_thumbnails.fields import ThumbnailerImageField

AUTH_USER_MODEL = get_user_model()

def get_timestamp_path(img, filename):
    timestamp = datetime.now().timestamp()
    return 'uploaded_images/{}'.format(timestamp)

class Image(models.Model):
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Файл изображения')
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey()
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_images', null=True, blank=True)
    uploaded = models.DateTimeField('Дата и время загрузки изображения', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['content_type', 'object_id', '-uploaded',]

    def __str__(self):
        if self.content_object:
            return '{}, {} ({})'.format(self.pk, self.content_object, self.content_type)
        else:
            self.delete()

class CoverThumbnail(models.Model):
    thumbnail_sm = ThumbnailerImageField(resize_source={'size': (200, 150), 'crop': 'scale',})
    thumbnail_lg = ThumbnailerImageField(resize_source={'size': (400, 300), 'crop': 'scale',})
    primary_image = models.OneToOneField(to=Image, on_delete=models.CASCADE, unique=True)

    class Meta:
        verbose_name = 'Миниатюра'
        verbose_name_plural = 'Миниатюры заглавных изображений'
        ordering = ['primary_image']
