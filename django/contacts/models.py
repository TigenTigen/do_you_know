from django.db import models
from django.contrib.auth import get_user_model

AUTH_USER_MODEL = get_user_model()

class Category(models.Model):
    title = models.CharField('Наименование категории', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Категория сообщений'
        verbose_name_plural = 'Категории сообщений'
        ordering = ['title']

    def __str__(self):
        return self.title

class Message(models.Model):
    title = models.CharField('Заголовок', max_length=30)
    text = models.TextField('Содержание сообщения')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)
    show_as_faq = models.BooleanField('Включено в FAQ', default=False)
    is_private = models.BooleanField('Личное сообщение', default=False)
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT, related_name='messages', verbose_name='Категория')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created']

    def __str__(self):
        return self.title

class UserMessage(Message):
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, related_name='messages', verbose_name='Зарегистрированный пользователь')
    message = models.OneToOneField(to=Message, on_delete=models.CASCADE, parent_link=True, related_name='reg_user')

    class Meta:
        verbose_name = 'Собщение зарегистрированного пользователя'
        verbose_name_plural = 'Сообщения зарегистрированных пользователей'

    def __str__(self):
        return '{} (Пользователь)'.format(self.user.username)

class AnonymousMessage(Message):
    email = models.EmailField('Адрес электронной почты')
    name = models.CharField('Имя', max_length=30)
    message = models.OneToOneField(to=Message, on_delete=models.CASCADE, parent_link=True, related_name='anon')

    class Meta:
        verbose_name = 'Анонимное сообщение'
        verbose_name_plural = 'Аннонимные сообщения'

    def __str__(self):
        return '{} (Гость)'.format(self.name)

class Reply(models.Model):
    text = models.TextField('Содержание ответа')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)
    user = models.ForeignKey(to=AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.ForeignKey(to=Message, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        verbose_name = 'Ответ на сообщение'
        verbose_name_plural = 'Ответы комманды сайта на сообщения'
