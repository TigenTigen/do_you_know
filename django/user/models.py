from django.db import models
from django.contrib.auth.models import User

# Данная прокси-модель заменит модель пользователя User, используемую по умолчанию.
# Данная замена должна быть отражена в настройках проекта: AUTH_USER_MODEl = 'user.models.AdvUser'.
# Замен производится с целью расширения стандартной модели с помощью дополнительных методов и атрибутов.
class AdvUser(User):
    class Meta:
        proxy = True
