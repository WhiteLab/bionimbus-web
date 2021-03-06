"""
Django settings for bionimbus_web project.

Generated by 'django-admin startproject' using Django 1.8.14.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from tina import urljoin
import tina_web.local_settings as local_settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'djangobower',
    'shibboleth',
    'tina',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shibboleth.middleware.ShibbolethRemoteUserMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'tina_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'tina_web.wsgi.application'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder'
]

AUTHENTICATION_BACKENDS = (
    'shibboleth.backends.ShibbolethRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# SHIBBOLETH_ATTRIBUTE_MAP = {
#     'shib-user': (True, "username"),
#     'shib-given-name': (True, "first_name"),
#     'shib-sn': (True, "last_name"),
#     'shib-mail': (False, "email"),
# }

SHIBBOLETH_ATTRIBUTE_MAP = {
    'name': (True, 'username')
}


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = local_settings.DATABASES

CHANNEL_LAYERS = local_settings.CHANNEL_LAYERS

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = local_settings.TIME_ZONE

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Prefixes for URLs
URL_HOSTNAME = local_settings.URL_HOSTNAME
RELATIVE_URL_PREFIX = local_settings.RELATIVE_URL_PREFIX

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# STATIC_URL = '/static/'
# STATIC_PATH = os.path.join(BASE_DIR, 'static')
# STATIC_ROOT = STATIC_PATH
#
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'

# LOGIN_URL = '/login/'
# LOGIN_URL = 'https://igsbconferences.uchicago.edu/Shibboleth.sso/Login'

STATIC_URL = urljoin('/', RELATIVE_URL_PREFIX, 'static')
STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = STATIC_PATH

MEDIA_URL = urljoin('/', RELATIVE_URL_PREFIX, 'media')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = urljoin(URL_HOSTNAME, 'Shibboleth.sso/Login')

# Bower Django settings
BOWER_COMPONENTS_ROOT = BASE_DIR

BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-toast-plugin#1.3.1',
    'handsontable#0.29.0',

    'bootstrap#3.3.7',
    'fontawesome',

    'bourbon#4.3.3',
    'neat#1.8.0',

    # 'polymer#^2.0.0', 'PolymerElements/iron-icon#^2.0.0'  Eventually move to Polymer 2.0
    'polymer#1.8.1', 'PolymerElements/iron-icon#^1.0.12',

    'lunr'

    # 'bottom-drawer'  # Polymer element
)

# CouchDB Settings
COUCH_SERVER = local_settings.COUCH_SERVER
COUCH_TINA_DB = local_settings.COUCH_TINA_DB

# Root directory where library fastqs will be stored
LIBRARY_DATA_ROOT = local_settings.LIBRARY_DATA_ROOT

# Application wide strings
STRINGS = {
    'app_name': 'Tina',
    'installed_app_name': 'tina'
}


