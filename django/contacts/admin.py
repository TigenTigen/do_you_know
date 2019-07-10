from django.contrib import admin
from django import forms
from contacts.models import *

class UserMessageInline(admin.StackedInline):
    model = UserMessage
    extra = 0
    fields = ('user',)
    readonly_fields = ('user',)

class AnonymousMessageInline(admin.StackedInline):
    model = AnonymousMessage
    extra = 0
    fields = ('name', 'email',)
    readonly_fields = ('name', 'email',)

class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 1
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 3})},}
    fields = ('text', 'user', 'created',)
    readonly_fields = ('created', 'user',)

class ReplyFilter(admin.SimpleListFilter):
    title = 'Ответ'
    parameter_name = 'replies'

    def lookups(self, request, model_admin):
        return (('True', 'Есть'), ('False', 'Нет'),)

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            if lookup_value == 'True':
                return queryset.filter(replies__isnull=False).distinct()
            elif lookup_value == 'False':
                return queryset.filter(replies__isnull=True).distinct()

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # list page
    list_display = ('id', 'title', 'show_as_faq', 'is_private', 'created', 'category', 'author', 'replies_status')
    list_display_links = ('title',)
    search_fields = ('=id', 'title',)
    list_filter = (ReplyFilter, 'category', 'show_as_faq', 'is_private', 'created',)
    date_hierarchy = 'created'
    # form page
    fields = (('category', 'show_as_faq',), ('title', 'text',), ('created', 'is_private',), )
    readonly_fields = ('title', 'text', 'created', 'is_private',)

    def author(self, rec):
        try:
            if rec.reg_user:
                return 'Пользователь'
        except:
            if rec.anon:
                return 'Гость'
    author.short_description = 'Автор'

    def replies_status(self, rec):
        if rec.replies.count() > 0:
            return 'Есть'
        return 'Нет'
    replies_status.short_description = 'Ответ'

    def get_inline_instances(self, request, obj=None):
        inlines = []
        try:
            if obj.reg_user:
                inlines.append(UserMessageInline(self.model, self.admin_site))
        except:
            if obj.anon:
                inlines.append(AnonymousMessageInline(self.model, self.admin_site))
        inlines.append(ReplyInline(self.model, self.admin_site))
        return tuple(inlines)
