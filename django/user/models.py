from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
from django.template import engines, Context
from django.urls import reverse
from django.db.models import Sum
from django.contrib.auth.models import UserManager
from django.core import mail
import os

HOST_NAME = os.getenv('HOST_NAME')
signer = Signer()
dt_engine = engines['django'].engine

# Данная sмодель заменит модель пользователя User, используемую по умолчанию.
# Данная замена должна быть отражена в настройках проекта: AUTH_USER_MODEL = 'user.models.AdvUser'.
# Замен производится с целью расширения стандартной модели с помощью дополнительных методов и атрибутов.
class AdvUserManager(UserManager):
    def get_points_rating_queryset(self):
        qs = self.get_queryset()
        qs = qs.filter(is_active=True)
        qs = qs.annotate(points_count=Sum('replies__points'))
        qs = qs.exclude(points_count=None)
        qs = qs.order_by('-points_count')
        return qs

class AdvUser(AbstractUser):
    objects = AdvUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи (расширенная модель)'
        ordering = ['-date_joined']
        unique_together = ['email']

    def __str__(self):
        if (not self.username or self.username == '') and self.first_name and self.last_name:
           self.username = '{} {}'.format(self.first_name, self.last_name)
           self.save()
        return self.username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self._state.adding or force_insert
        if self.email:
            if self.email.strip() == '':
                self.email = None
            else:
                self.email = self.email.lower()
        if is_new and self.username.startswith('id'):
            self.username = '{} {}'.format(self.first_name, self.last_name)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def confirm(self):
        self.is_active = True
        self.save()

    def get_email_context(self):
        host = 'http://' + HOST_NAME
        sign = signer.sign(self.username)
        link = host + reverse('user:registration_confirmed', kwargs={'sign': sign})
        return Context({'confirmation_link': link})

    def send_confirmation_email(self, connection = None):
        context = self.get_email_context()
        text_body = dt_engine.get_template('emails/confirmation.txt').render(context=context)
        html_body = dt_engine.get_template('emails/confirmation.html').render(context=context)
        self.email_user(subject='Подтверждение регистрации', message=text_body, html_message=html_body, connection=connection)
        # not None connection parameter is used during tests, see tests/test_models.py - test_send_confirmation_email
        if connection:
            return mail.outbox

    def social_count(self):
        return self.social_auth.count()

    # questions
    def total_points_count(self):
        total_points_count = self.replies.aggregate(sum=models.Sum('points'))
        return total_points_count['sum'] or 0
