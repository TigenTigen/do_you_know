from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from social_django.models import UserSocialAuth
from django.db.models import Count

USER_MODEL = get_user_model()

class SocalAuthInline(admin.TabularInline):
    model = UserSocialAuth
    fields = ('provider', 'uid',)
    readonly_fields = ('provider', 'uid',)
    extra = 0
    can_delete = False
    show_change_link = False
    verbose_name = 'Вход через социальную сеть'
    verbose_name_plural = 'Вход через социальную сеть'

    def has_add_permission(self, request, obj=None):
        return False

class SocialAuthListFilter(admin.SimpleListFilter):
    title = 'Вход через социальные сети'
    parameter_name = 'social_count'

    def lookups(self, request, model_admin):
        return (('Да', 'Да'), ('Нет', 'Нет'),)

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value == 'Да':
            return queryset.exclude(social_count_ann=0)
        elif lookup_value == 'Нет':
            return queryset.filter(social_count_ann=0)

class UserAdmin(admin.ModelAdmin):
    # list settings
    list_display = ('id', 'username', 'email', 'is_active', 'date_joined', 'social_count')
    list_display_links = ('username',)
    search_fields = ('id', 'email', 'username')
    list_filter = ('is_active', 'date_joined', SocialAuthListFilter,)
    date_hierarchy = 'date_joined'
    list_per_page = 20
    inlines = (SocalAuthInline,)
    actions = ('resend_confirmation_emails',)

    # single form_page settings
    readonly_fields = ('is_active', 'password', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(social_count_ann=Count('social_auth'))

    def get_fields(self, request, obj=None):
        fields = [
            ('username', 'email', 'is_active',),
            'password', 'first_name', 'last_name',
            ('is_staff', 'is_superuser',),
            ('date_joined', 'last_login'),
        ]
        if Group.objects.exists():
            fields.append('groups')
        return fields

    # actions
    def resend_confirmation_emails(self, request, queryset):
        email_count = 0
        for user in queryset:
            if not user.is_active:
                user.send_confirmation_email()
                email_count = email_count + 1
        message_text = 'В адрес неактивированных пользователей направлено {} писем о подтверждении регистрации'
        self.message_user(request, message_text.format(email_count))
    resend_confirmation_emails.short_description = 'Направить повторное письмо о подвтерждении регистрации'

admin.site.register(USER_MODEL, UserAdmin)
