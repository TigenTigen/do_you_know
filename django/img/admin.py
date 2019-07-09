from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from img.models import Image

class ContentTypeListFilter(admin.SimpleListFilter):
    title = 'Тип связанного объекта'
    parameter_name = 'content_type'

    def lookups(self, request, model_admin):
        return (
            ('theme', 'Тема'),
            ('book', 'Книга'),
            ('movie', 'Фильм'),
            ('person', 'Человек'),
        )

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            content_type = ContentType.objects.get(app_label='core', model=lookup_value)
            return queryset.filter(content_type=content_type)

class ImageAdmin(admin.ModelAdmin):
    # list page
    list_display = ('id', 'content_object', 'content_type', 'user', 'uploaded', 'is_cover',)
    list_display_links = ('id',)
    list_select_related = ('user', 'content_type',)
    ordering = ('-uploaded',)
    search_fields = ('=id', '=user__username',)
    list_filter = (ContentTypeListFilter, 'uploaded', 'is_cover',)
    date_hierarchy = 'uploaded'

    #form page
    fields = (('image', 'is_cover',), ('content_object', 'content_type', 'object_id'), ('uploaded', 'user',),)
    readonly_fields = ('content_object', 'content_type', 'object_id', 'uploaded', 'user',)
    view_on_site = True

    def get_queryset(self, request):
        Image.objects.check_images()
        qs = super().get_queryset(request)
        return qs

admin.site.register(Image, ImageAdmin)
