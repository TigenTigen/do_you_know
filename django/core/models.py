from django.db import models
from django.contrib.auth import get_user_model

AUTH_USER_MODEL = get_user_model()

class PersonManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.prefetch_related('directed', 'wrote', 'roles', 'created',
                                 'written_books', 'character_set', 'acted_by')
        return qs

class Person(models.Model):
    is_fictional = models.BooleanField('Выдуманный персонаж', default = False)
    name = models.CharField('Имя', max_length = 100)
    born = models.DateField('Дата рождения', null = True, blank = True)
    died = models.DateField('Дата смерти', null = True, blank = True)
    description = models.TextField('Описание', null = True, blank = True)

    objects = PersonManager()

    class Meta:
        verbose_name = 'Человек'
        verbose_name_plural = 'Люди'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/core/persons/{}'.format(self.pk)

class BookManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.select_related('author')
        qs = qs.prefetch_related('characters', 'number_set')
        return qs

class Book(models.Model):
    GENRE_CHOICES = {
    (0, 'Фентези'),
    (1, 'Фантастика'),
    (2, 'Комедия'),
    (3, 'Драма'),
    }

    title = models.CharField('Название', max_length = 100)
    plot = models.TextField('Сюжет', null = True, blank = True)
    genre = models.PositiveIntegerField('Жанр', choices = GENRE_CHOICES, null = True, blank = True)
    year = models.PositiveIntegerField('Год публикации', null = True, blank = True)
    author = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'written_books', null = True, blank = True)
    characters = models.ManyToManyField(Person, through = 'Character', related_name = 'appeared_in', blank = True)

    objects = BookManager()

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        if self.year:
            return '{} ({})'.format(self.title, self.year)
        return self.title

    def get_absolute_url(self):
        return '/core/books/{}'.format(self.pk)

class Character(models.Model):
    is_main = models.BooleanField('Главный герой', default = False)
    character = models.ForeignKey(Person, on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE)
    description = models.TextField('Описание', null = True, blank = True)

    class Meta:
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'
        ordering = ('is_main', 'character')

    def __str__(self):
        return self.character.name

class MovieManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.select_related('director', 'writer')
        qs = qs.prefetch_related('roles', 'number_set')
        return qs

class Movie(models.Model):
    GENRE_CHOICES = {
    (0, 'Фентези'),
    (1, 'Фантастика'),
    (2, 'Комедия'),
    (3, 'Драма'),
    }

    title = models.CharField('Название', max_length = 100)
    plot = models.TextField('Сюжет', null = True, blank = True)
    genre = models.PositiveIntegerField('Жанр', choices = GENRE_CHOICES, null = True, blank = True)
    year = models.PositiveIntegerField('Год публикации', null = True, blank = True)
    director = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'directed', null = True, blank = True)
    writer = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'wrote', null = True, blank = True)
    actors = models.ManyToManyField(Person, through = 'Role', through_fields=('movie', 'actor'), related_name = 'acted_in', blank = True)

    objects = MovieManager()

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['title']

    def __str__(self):
        if self.year:
            return '{} ({})'.format(self.title, self.year)
        return self.title

    def get_absolute_url(self):
        return '/core/movies/{}'.format(self.pk)

class Role(models.Model):
    is_main = models.BooleanField('Главный герой', default = False)
    description = models.TextField('Описание', null = True, blank = True)
    movie = models.ForeignKey(Movie, related_name = 'roles', on_delete = models.CASCADE)
    actor = models.ForeignKey(Person, related_name = 'roles', on_delete = models.CASCADE)
    character = models.ForeignKey(Person, related_name = 'acted_by', on_delete = models.SET_NULL, null = True, blank = True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ('is_main', 'actor')

    def __str__(self):
        return '{} сыграл(а) {}'.format(self.actor.name, self.character.name)

class Cycle(models.Model):
    title = models.CharField('Название', max_length = 100)
    description = models.TextField('Описание', null = True, blank = True)

    class Meta:
        verbose_name = 'Цикл'
        verbose_name_plural = 'Циклы'
        ordering = ['title']

    def __str__(self):
        return self.title

class Number(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE, null = True, blank = True)
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE, null = True, blank = True)
    number = models.PositiveIntegerField('Порядковый номер в серии')

    class Meta:
        verbose_name = 'Участник цикла'
        verbose_name_plural = 'Участники циклов'
        ordering = ('cycle', 'number')
        unique_together = ('cycle' , 'number')

    def __str__(self):
        return '{} #{}'.format(self.cycle, str(self.number))

class ThemeManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.prefetch_related('creators', 'cycles', 'books', 'movies')
        return qs

class Theme(models.Model):
    title = models.CharField('Название', max_length = 100)
    description = models.TextField('Описание', null = True, blank = True)
    creators = models.ManyToManyField(Person, related_name = 'created', blank = True)
    cycles = models.ManyToManyField(Cycle, blank = True)
    books = models.ManyToManyField(Book, blank = True)
    movies = models.ManyToManyField(Movie, blank = True)

    objects = ThemeManager()

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ['id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/core/themes/{}'.format(self.pk)
