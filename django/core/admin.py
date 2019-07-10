from django.contrib import admin
from django.db.models import Q
from django import forms
from core.models import *

class ValidationFilter(admin.SimpleListFilter):
    title = 'Валидация'
    parameter_name = 'validation'

    def lookups(self, request, model_admin):
        return (
            ('validated', 'Одобрено'),
            ('validated_by_staff', 'Одобрено командой сайта'),
            ('validated_by_users', 'Одобрено голосованием пользователей'),
            ('awaiting', 'Ожидают одобрения'),
        )

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            lookup_dict = {
                'validated': queryset.filter(Q(is_validated_by_staff=True) | Q(is_validated_by_users=True)),
                'validated_by_staff': queryset.filter(is_validated_by_staff=True),
                'validated_by_users': queryset.filter(is_validated_by_users=True),
                'awaiting': queryset.exclude(Q(is_validated_by_staff=True) | Q(is_validated_by_users=True)),
            }
            return lookup_dict[lookup_value]

class ValidatableModelAdmin(admin.ModelAdmin):
    # list page
    list_display = ('id', 'title',)
    list_display_links = ('title',)
    search_fields = ('=id', 'title',)
    list_filter = (ValidationFilter,)
    # form page
    view_on_site = True
    fields = ['title', 'description', 'user', 'proposed', 'validated',
              ('is_validated_by_users', 'is_validated_by_staff', 'staff',),
              ('approve_score', 'rating',),]
    readonly_fields = ('user', 'proposed', 'validated', 'is_validated_by_users', 'is_validated_by_staff', 'staff', 'approve_score', 'rating',)

    def get_list_display(self, request):
        list_display = list(self.list_display)
        validation_filter = request.GET.get('validation')
        if validation_filter == 'awaiting':
            list_display.extend(['approve_score', 'proposed',])
            return tuple(list_display)
        elif not validation_filter or validation_filter == 'validated':
            list_display.append('validation_status')
        list_display.append('rating')
        try:
            list_display.extend(self.list_display_extra)
        except:
            pass
        return tuple(list_display)

    def get_fields(self, request, obj=None):
        fields = list(self.fields)
        try:
            i = 2
            for one in self.extra_fields:
                fields.insert(i, one)
                i = i + 1
        except:
            pass
        return tuple(fields)

@admin.register(Theme)
class ThemeAdmin(ValidatableModelAdmin):
    list_display_extra = ['favorite_count',]

@admin.register(Book, Movie)
class BookAdmin(ValidatableModelAdmin):
    extra_fields = ['genre', 'year',]

class BookCharacterInline(admin.TabularInline):
    model = Character
    extra = 0
    fields = ('book', 'is_main', 'description',)
    readonly_fields = ('book',)
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 3})},}

    def view_on_site(self, rec):
        return rec.book.get_absolute_url()

class MovieCharacterInline(admin.TabularInline):
    model = Role
    verbose_name = 'Персонаж'
    verbose_name_plural = 'Появления в фильмах'
    fk_name = 'character'
    extra = 0
    fields = ('movie', 'actor', 'is_main', 'description',)
    readonly_fields = ('movie', 'actor',)
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 3})},}

    def view_on_site(self, rec):
        return rec.movie.get_absolute_url()

class ActorInline(admin.TabularInline):
    model = Role
    verbose_name = 'Роль'
    verbose_name_plural = 'Роли'
    fk_name = 'actor'
    extra = 0
    fields = ('movie', 'character', 'is_main', 'description',)
    readonly_fields = ('movie', 'character',)
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 3})},}

    def view_on_site(self, rec):
        return rec.movie.get_absolute_url()

@admin.register(Person)
class PersonAdmin(ValidatableModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('name',)
    search_fields = ('=id', 'name',)
    fields = [('name', 'is_fictional',), ('born', 'died',), 'description', 'user', 'proposed', 'validated',
              ('is_validated_by_users', 'is_validated_by_staff', 'staff',),
              ('approve_score', 'rating',),]
    #inlines = (BookCharacterInline, MovieCharacterInline, ActorInline,)

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj.character_set.exists():
            inlines.append(BookCharacterInline(self.model, self.admin_site))
        if obj.acted_by.exists():
            inlines.append(MovieCharacterInline(self.model, self.admin_site))
        if obj.roles.exists():
            inlines.append(ActorInline(self.model, self.admin_site))
        return tuple(inlines)

class NumberInline(admin.TabularInline):
    model = Number
    ordering = ('number',)
    extra = 1
    view_on_site = False

    def get_fields(self, request, obj=None):
        if obj.number_set.first().book:
            return ('number', 'book')
        elif obj.number_set.first().movie:
            return ('number', 'movie')

class ThemeFilter(admin.SimpleListFilter):
    title = 'Тема'
    parameter_name = 'theme'

    def get_themes(self):
        return Theme.objects.filter(cycles__isnull=False).distinct()

    def lookups(self, request, model_admin):
        lookups = []
        for theme in self.get_themes():
            lookups.append((theme.id, theme.title,))
        return tuple(lookups)

    def queryset(self, request, queryset):
        lookup_value = self.value()
        if lookup_value:
            return queryset.filter(theme__id=lookup_value)

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'number_count',)
    list_display_links = ('title',)
    list_filter = (ThemeFilter,)
    search_fields = ('=id', 'title',)
    inlines = [NumberInline]

    def number_count(self, rec):
        return rec.number_set.count()
    number_count.short_description = 'Количество частей'

class QuestionThemeFilter(ThemeFilter):
    def get_themes(self):
        return Theme.objects.filter(theme_questions__isnull=False).distinct()

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

@admin.register(Question)
class Question(admin.ModelAdmin):
    list_display = ('id', 'text', 'theme', 'user', 'created', 'rating',)
    list_display_links = ('id',)
    list_select_related = ('theme', 'user',)
    list_filter = (QuestionThemeFilter,)
    search_fields = ('=id', 'text', '^theme__title', '^user__username',)
    date_hierarchy = 'created'
    fields = ('theme', ('text', 'explanation',), ('user', 'created',),)
    readonly_fields = ('theme', 'user', 'created',)
    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'rows': 3})},}
    inlines = (AnswerInline,)
