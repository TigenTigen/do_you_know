from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.signing import Signer
from django.template import engines, Context
from django.urls import reverse
from django.db.models import Count

ALLOWED_HOSTS = settings.ALLOWED_HOSTS
signer = Signer()
dt_engine = engines['django'].engine

# Данная sмодель заменит модель пользователя User, используемую по умолчанию.
# Данная замена должна быть отражена в настройках проекта: AUTH_USER_MODEL = 'user.models.AdvUser'.
# Замен производится с целью расширения стандартной модели с помощью дополнительных методов и атрибутов.
class AdvUserManager(models.Manager):
    pass

class AdvUser(AbstractUser):
    #objects = AdvUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи (расширенная модель)'
        ordering = ['-date_joined']

    def __str__(self):
        if self.username.startswith('id'):
            if self.first_name != '' and self.last_name != '':
                self.username = '{} {}'.format(self.first_name, self.last_name)
                self.save()
        return self.username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self._state.adding or force_insert
        if is_new and self.username.startswith('id'):
            self.username = '{} {}'.format(self.first_name, self.last_name)
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def confirm(self):
        self.is_active = True
        self.save()

    def get_email_context(self):
        if ALLOWED_HOSTS and ALLOWED_HOSTS != []:
            host = 'http://' + ALLOWED_HOSTS[0]
        else:
            host = 'http://localhost:8000'
        sign = signer.sign(self.username)
        link = host + reverse('user:registration_confirmed', kwargs={'sign': sign})
        return Context({'confirmation_link': link})

    def send_confirmation_email(self):
        context = self.get_email_context()
        text_body = dt_engine.get_template('emails/confirmation.txt').render(context=context)
        html_body = dt_engine.get_template('emails/confirmation.html').render(context=context)
        self.email_user(subject='Подтверждение регистрации', message=text_body, html_message=html_body)

    def social_count(self):
        return self.social_auth.count()
