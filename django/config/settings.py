"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '37=6z_k6=jce#o1-ho*+snml236uaj8)6j^rcfr67kxtb6rh_('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'do_you_know',
        'USER': 'postgres',
        'PASSWORD': 'passwordforpostgresql',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'ATOMIC_REQUEST': True,
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Krasnoyarsk'

USE_I18N = True

USE_L10N = False # disable datetime and numeric internationalization

USE_TZ = True

# Параметры ввода и вывода дат: задано вручную (при отключении USE_L10N)
DATE_FORMAT = "d.m.Y"
DATE_INPUT_FORMATS = ['%d.%m.%Y']
SHORT_DATE_FORMAT = "d.m.Y"

DATETIME_FORMAT = "d.m.Y H:i:s"
DATETIME_INPUT_FORMATS = ["%d.%m.%Y %H:%M:%S"]
SHORT_DATETIME_FORMAT = "d.m.Y H:M:s"

TIME_FORMAT = "H:M"
TIME_INPUT_FORMATS = ["%H:%M"]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# crispy_forms settings:
INSTALLED_APPS += ['crispy_forms',]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# user settings
INSTALLED_APPS = ['user.apps.UserConfig',] + INSTALLED_APPS
AUTH_USER_MODEL = 'user.AdvUser'
LOGIN_URL = 'accounts/login/' # адрес, ведущий на страницу входа
LOGIN_REDIRECT_URL = 'main_page' # адрес, на который произойдет перенаправление после входа
LOGOUT_REDIRECT_URL = 'main_page' # адрес, на который произойдет перенаправление после выхода
                           # если None, перенаправление не произойдет, будет выведена страница выхода с сайта

# Mail settings (for registration confirmation emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'djangomailape@gmail.com'
EMAIL_HOST_PASSWORD = 'letsspam'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@do_you_know.com'
MAILING_LIST_LINK_DOMAIN = 'http://127.0.0.1:8000'

# social-django settings
INSTALLED_APPS += ['social_django',]
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
TEMPLATES[0]['OPTIONS']['context_processors'].append('social_django.context_processors.backends')
TEMPLATES[0]['OPTIONS']['context_processors'].append('social_django.context_processors.login_redirect')
AUTHENTICATION_BACKENDS = (
    'social_core.backends.vk.VKOAuth2',                 # for vk
    'django.contrib.auth.backends.ModelBackend',
)

# ... for vk:
SOCIAL_AUTH_VK_OAUTH2_KEY = '7031159'
SOCIAL_AUTH_VK_OAUTH2_SECRET = 'cJRcIxvV9xLPtgg84UeE'
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']
