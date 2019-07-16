from django.db import models
from django.db.models import Q, F, Count, Case, When, Avg, Sum
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import datetime

from img.models import *

AUTH_USER_MODEL = get_user_model()

class QuestionManager(models.Manager):
    def get_random_question(self, user):
        questions = self.get_queryset()
        questions = questions.exclude(user=user).exclude(replies__user=user)
        if not questions.exists():
            return None
        return questions.order_by('?').first()

    def get_wellcome_question(self):
        qs = self.get_queryset()
        qs = self.order_by('-rating')
        return qs.first()

    def user_created(self, user):
        qs = self.get_queryset()
        qs = qs.filter(user=user)
        return qs

class Question(models.Model):
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    theme = models.ForeignKey(to='Theme', on_delete=models.CASCADE, related_name='theme_questions', null=True, blank=True, verbose_name='Тема')
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор вопроса')
    created = models.DateTimeField('Дата создания пользователем', auto_now_add=True)
    text = models.TextField('Текст вопроса')
    explanation = models.TextField('ОбЪяснения ответа', null=True, blank=True)
    # rating
    rating = models.FloatField('Оценка пользователей', default=0)
    ratings = GenericRelation(to='Rating', related_name='object')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = '6. Вопросы'
        ordering = ['-created']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return '/core/questions/{}'.format(self.pk)

    def right_answer(self):
        right_answer = self.answers.filter(is_right=True)
        if right_answer.count() != 1:
            self.delete()
        else:
            return right_answer.get()

    def refresh_ratig(self):
        aggregation_dict = self.ratings.aggregate(rating=Avg('value'))
        self.rating = aggregation_dict.get('rating')
        self.save()

class Answer(models.Model):
    text = models.CharField('Текст ответа', max_length=100)
    is_right = models.BooleanField('Правильный ответ', default=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name='answers')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['question', 'text']

    def __str__(self):
        return self.text

    def color(self):
        if self.is_right:
            return 'text-success'
        return 'text-dark'

    def frequence(self):
        replies_for_this_question = self.question.replies.count()
        if replies_for_this_question != 0:
            replies_for_this_answer = self.replies.count()
            frequence = (replies_for_this_answer / replies_for_this_question)*100
            return frequence
        return 0

    def points(self):
        if self.is_right:
            return (100 - self.frequence())/10 + 1
        return 0

class UserReplyRecord(models.Model):
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='replies')
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name='replies')
    answer = models.ForeignKey(to=Answer, on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    timedate = models.DateTimeField('Дата ответа', auto_now_add=True)
    outcome = models.BooleanField('Результат проверки ответа', default=None, null=True, blank=True)
    points = models.PositiveIntegerField('Очки, полученные пользователем за правильный ответ', default=0)

    class Meta:
        verbose_name = 'Ответ пользователя на вопрос'
        verbose_name_plural = 'Ответы пользователей на вопросы'
        unique_together = ['user', 'question', 'answer']

class Rating(models.Model):
    value = models.PositiveSmallIntegerField('', default=0)
    user_rated = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = 'Оценка пользователя'
        verbose_name_plural = 'Оценки пользователей страниц сайта'
        unique_together = ['user_rated', 'content_type', 'object_id']

    def __str__(self):
        return str(self.value)

class ValidatableModelManager(models.Manager):
    def passed(self):
        qs = self.get_queryset()
        qs = qs.filter(Q(is_validated_by_staff=True) | Q(is_validated_by_users=True))
        return qs

    def current(self, user):
        qs = self.get_queryset()
        qs = qs.exclude(Q(is_validated_by_staff=True) | Q(is_validated_by_users=True))
        if user.is_authenticated:
            qs = qs.annotate(vote_count=Count('user_voted', filter=Q(user_voted=user), distinct=True),
                             already_voted=Case(When(vote_count=0, then=False), default=True, output_field=models.BooleanField()),
                             user_is_creator=Case(When(created_by_user_id=user.id, then=True), default=False, output_field=models.BooleanField()))
        return qs

    def user_created(self, user_id):
        qs = self.get_queryset()
        qs = qs.filter(created_by_user_id=user_id)
        return qs

class ValidatableModel(models.Model):
    # validation
    approve_score = models.SmallIntegerField('Счетчик одобрения', default=0)
    is_validated_by_staff = models.BooleanField('Одобрен командой сайта', default=False)
    is_validated_by_users = models.BooleanField('Одобрен пользовательским голосованием', default=False)
    proposed = models.DateTimeField('Дата вынесения на одобрение', auto_now_add=True, null=True, blank=True)
    validated = models.DateTimeField('Дата одобрения', null=True, blank=True)
    created_by_user_id = models.SmallIntegerField('Пользователь, создавший данный объект', null=True, blank=True) # на ForeignKey джанго ругается
    validated_by_staff_id = models.SmallIntegerField('Член команды сайта, одобривший данный объект', null=True, blank=True) # на ForeignKey джанго ругается
    user_voted = models.ManyToManyField(to=AUTH_USER_MODEL)
    # rating
    rating = models.FloatField('Оценка пользователей', default=0)
    ratings = GenericRelation(Rating, related_name='object')
    # images
    images = GenericRelation(Image, related_name='object')
    # questions
    questions = GenericRelation(Question, related_name='object')

    validation = ValidatableModelManager()

    class Meta:
        abstract = True

    def is_validated(self):
        return (self.is_validated_by_staff or self.is_validated_by_users)

    def color(self):
        if self.is_validated():
            return 'text-dark'
        return 'text-muted'

    def user(self):
        return AUTH_USER_MODEL.objects.get(id=self.created_by_user_id)
    user.short_description = 'Пользователь, создавший данную страницу'

    def staff(self):
        return AUTH_USER_MODEL.objects.get(id=self.validated_by_staff_id)
    staff.short_description = 'Член команды сайта, утвердивший данную страницу'

    def target(self):
        return 5

    def validated_by_staff(self, user):
        self.is_validated_by_staff = True
        self.validated = datetime.now()
        self.validated_by_staff_id = user.id
        self.save()

    def approved(self, user):
        self.approve_score = self.approve_score + 1
        self.user_voted.add(user)
        if self.approve_score >= self.target():
            self.is_validated_by_users = True
            self.validated = datetime.now()
        self.save()

    def disapproved(self, user):
        self.approve_score = self.approve_score - 1
        self.user_voted.add(user)
        self.save()

    def validation_status(self):
        if self.is_validated_by_staff:
            return 'одобрено командой сайта'
        elif self.is_validated_by_users:
            return 'одобрено по итогам голосования пользователей'
        return 'текущий уровень одобрения: {}'.format(self.approve_score)
    validation_status.short_description = 'Валидация'

    def refresh_ratig(self):
        aggregation_dict = self.ratings.aggregate(rating=Avg('value'))
        self.rating = aggregation_dict.get('rating')
        self.save()

    def img_preview_set(self):
        return self.images.all()[:4:]

    def cover_img(self):
        cover_img = self.images.filter(is_cover=True)
        if cover_img.exists():
            return cover_img.get()
        return self.images.last()

    def get_question_to_ask(self, user):
        questions = self.questions.exclude(user=user).exclude(replies__user=user)
        if not questions.exists():
            return None
        return questions.first()

class PersonManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.prefetch_related('directed', 'wrote', 'roles', 'created',
                                 'written_books', 'character_set', 'acted_by')
        return qs

class CustomValidatableModelManager(ValidatableModelManager):
    def passed(self):
        qs = self.get_queryset()
        qs = qs.filter(Q(is_validated_by_staff=True) | Q(is_validated_by_users=True))
        qs = qs.annotate(title=F('name'), year=F('born'))
        return qs

class Person(ValidatableModel):
    is_fictional = models.BooleanField('Выдуманный персонаж', default = False)
    name = models.CharField('Имя', unique=True, max_length = 100)
    born = models.DateField('Дата рождения', null = True, blank = True)
    died = models.DateField('Дата смерти', null = True, blank = True)
    description = models.TextField('Описание', null = True, blank = True)

    objects = PersonManager()
    validation = CustomValidatableModelManager()

    class Meta:
        verbose_name = 'Человек'
        verbose_name_plural = '4. Люди'
        ordering = ['name']

    def __str__(self):
        return self.name

    def extras(self):
        dict = {'Дата рождения': self.born, 'Дата смерти': self.died,}
        if self.is_fictional:
            dict.update({'Вымышленный персонаж': 'Да'})
        return dict

    def get_absolute_url(self):
        return '/core/persons/{}/'.format(self.pk)

    def model(self):
        return 'Person'

class BookManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.select_related('author')
        qs = qs.prefetch_related('characters', 'number_set')
        return qs

class Book(ValidatableModel):
    GENRE_CHOICES = {
    (0, 'Фентези'),
    (1, 'Фантастика'),
    (2, 'Комедия'),
    (3, 'Драма'),
    }

    title = models.CharField('Название', unique=True, max_length = 100)
    description = models.TextField('Сюжет', null = True, blank = True)
    genre = models.PositiveIntegerField('Жанр', choices = GENRE_CHOICES, null = True, blank = True)
    year = models.PositiveIntegerField('Год публикации', null = True, blank = True)
    author = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'written_books', null = True, blank = True)
    characters = models.ManyToManyField(Person, through = 'Character', related_name = 'appeared_in', blank = True)

    objects = BookManager()

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = '2. Книги'
        ordering = ['title']

    def __str__(self):
        if self.year:
            return '{} ({})'.format(self.title, self.year)
        return self.title

    def extras(self):
        dict = {'Жанр': self.get_genre_display(),}
        if self.author and self.author.is_validated():
            dict.update({'Автор': self.author,})
        return dict

    def get_absolute_url(self):
        return '/core/books/{}/'.format(self.pk)

    def model(self):
        return 'Book'

class Character(models.Model):
    is_main = models.BooleanField('Главный герой', default = False)
    character = models.ForeignKey(Person, on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE, verbose_name='Книга')
    description = models.TextField('Описание', null = True, blank = True)

    class Meta:
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'
        ordering = ('is_main', 'character')
        unique_together = ['character', 'book']

    def __str__(self):
        return self.character.name

    def get_absolute_url(self):
        return self.character.get_absolute_url()

class MovieManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.select_related('director', 'writer')
        qs = qs.prefetch_related('roles', 'number_set')
        return qs

class Movie(ValidatableModel):
    GENRE_CHOICES = {
    (0, 'Фентези'),
    (1, 'Фантастика'),
    (2, 'Комедия'),
    (3, 'Драма'),
    }

    title = models.CharField('Название', unique=True, max_length = 100)
    description = models.TextField('Сюжет', null = True, blank = True)
    genre = models.PositiveIntegerField('Жанр', choices = GENRE_CHOICES, null = True, blank = True)
    year = models.PositiveIntegerField('Год публикации', null = True, blank = True)
    director = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'directed', null = True, blank = True)
    writer = models.ForeignKey(Person, on_delete = models.SET_NULL, related_name = 'wrote', null = True, blank = True)
    actors = models.ManyToManyField(Person, through = 'Role', through_fields=('movie', 'actor'), related_name = 'acted_in', blank = True)

    objects = MovieManager()

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = '3. Фильмы'
        ordering = ['title']
        unique_together = ['title', 'year']

    def __str__(self):
        if self.year:
            return '{} ({})'.format(self.title, self.year)
        return self.title

    def extras(self):
        dict = {'Жанр': self.get_genre_display(),}
        if self.director and self.director.is_validated():
            dict.update({'Режисер': self.director,})
        if self.writer and self.writer.is_validated():
            dict.update({'Сценарист': self.writer,})
        return dict

    def get_absolute_url(self):
        return '/core/movies/{}/'.format(self.pk)

    def model(self):
        return 'Movie'

class Role(models.Model):
    is_main = models.BooleanField('Главный герой', default = False)
    description = models.TextField('Описание', null = True, blank = True)
    movie = models.ForeignKey(Movie, related_name = 'roles', on_delete = models.CASCADE, verbose_name='Фильм')
    actor = models.ForeignKey(Person, related_name = 'roles', on_delete = models.CASCADE, verbose_name='Актер')
    character = models.ForeignKey(Person, related_name = 'acted_by', on_delete = models.SET_NULL, null = True, blank = True, verbose_name='Персонаж')

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ('is_main', 'actor')
        unique_together = ['movie', 'actor', 'character']

    def __str__(self):
        return '{} сыграл(а) {}'.format(self.actor.name, self.character.name)

class CycleManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.prefetch_related('number_set')
        return qs

class Cycle(models.Model):
    title = models.CharField('Название', unique=True, max_length = 100)
    description = models.TextField('Описание', null = True, blank = True)

    objects = CycleManager()

    class Meta:
        verbose_name = 'Цикл'
        verbose_name_plural = '5. Циклы'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/core/cycles/{}'.format(self.pk)

class Number(models.Model):
    cycle = models.ForeignKey(Cycle, on_delete = models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE, null = True, blank = True, verbose_name='Книга')
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE, null = True, blank = True, verbose_name='Фильм')
    number = models.PositiveIntegerField('Порядковый номер в серии')

    class Meta:
        verbose_name = 'Участник цикла'
        verbose_name_plural = 'Участники циклов'
        ordering = ('cycle', 'number')
        unique_together = ('cycle' , 'number')

    def __str__(self):
        return '{} #{}'.format(self.cycle, str(self.number))

    def object(self):
        if self.book:
            return self.book
        if self.movie:
            return self.movie
        self.delete()

    def get_absolute_url(self):
        return self.cycle.get_absolute_url()

class ThemeManager(models.Manager):
    def all_with_perfetch(self):
        qs = self.get_queryset()
        qs = qs.prefetch_related('creators', 'cycles', 'books', 'movies')
        return qs

class ValidationThemeManager(ValidatableModelManager):
    def favorite_by(self, user):
        qs = self.get_queryset()
        qs = qs.filter(favorited_by=user).distinct()
        return qs

class Theme(ValidatableModel):
    title = models.CharField('Название', unique=True, max_length = 100)
    description = models.TextField('Описание', null = True, blank = True)
    creators = models.ManyToManyField(Person, related_name = 'created', blank = True)
    cycles = models.ManyToManyField(Cycle, blank = True, related_name='theme')
    books = models.ManyToManyField(Book, blank = True)
    movies = models.ManyToManyField(Movie, blank = True)
    favorited_by = models.ManyToManyField(AUTH_USER_MODEL, related_name='favorite_themes')

    objects = ThemeManager()
    validation = ValidationThemeManager()

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = '1. Темы'
        ordering = ['id']

    def extras(self):
        list = []
        for person in self.creators.all():
            if person.is_validated():
                list.append(person.name)
        if list != []:
            return {'Создатели': ', '.join(list)}
        return None

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/core/themes/{}/'.format(self.pk)

    def model(self):
        return 'Theme'

    def favorite_count(self):
        return self.favorited_by.distinct().count()
    favorite_count.short_description = 'Избарнная тема'

    def get_question_to_ask(self, user):
        questions = self.theme_questions.all()
        questions = questions.exclude(user=user).exclude(replies__user=user)
        if not questions.exists():
            return None
        return questions.first()
