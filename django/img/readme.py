Универсальный блок по работе с изображениями.

Установка:
1. Скопировать папку с приложением в папку проекта
2. Добавить в перечень необходимых библиотек: pillow, easy-thumbnails, django-cleanup, requests. Устанавливаем их с помощью pip.
2. Добавить в файл настроек settings следующие строки:
    # img settings
    INSTALLED_APPS += ['img.apps.ImgConfig', 'django_cleanup', 'easy_thumbnails', ]
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    THUMBNAIL_BASEDIR = 'thumbnails'
    THUMBNAIL_ALIASES = {
        '': {
            'default': {
                'size': (100, 100),
                'crop': 'scale',
            },
        },
    }

3. Добавить в файл urls следующий маршрут:
    path('img/', include('img.urls', namespace='img'))

    #from django.conf.urls.static import static
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

4. Добавить поля связи с моделями Изображений к необходимым моделям основного приложения:
    # from django.contrib.contenttypes.fields import GenericRelation
    cover_img = models.ForeignKey(to=CoverThumbnail, on_delete=models.PROTECT, null=True, blank=True)
    images = GenericRelation(Image, related_name='object')

5. Добавить стандартные шаблоны изображений в основные шаблоны:
    {% include 'img/img_preview_set.html' with img_preview_set=object.img_preview_set %}
    {% include 'img/image_upload_form.html' %}
