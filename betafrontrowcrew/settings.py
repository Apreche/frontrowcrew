"""
Django settings for betafrontrowcrew project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from . import utils

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "BETAFRONTROWCREW_SECRET_KEY",
    "django-insecure-gfzme-rm0l_7k_n)-$8yillmpe#mwlw@e&*l1%3(f^r4-ul=!=",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = utils.str_to_bool(os.environ.get("BETAFRONTROWCREW_DEBUG", "True"))


ALLOWED_HOSTS = []
extra_hosts = os.environ.get("BETAFRONTROWCREW_HOSTS", None)
if extra_hosts:
    ALLOWED_HOSTS += extra_hosts.split(",")
INTERNAL_IPS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_beat",
    "django_celery_results",
    "django_extensions",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE

ROOT_URLCONF = "betafrontrowcrew.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "betafrontrowcrew.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("BETAFRONTROWCREW_DB_NAME", "betafrontrowcrew"),
            "USER": os.environ.get("BETAFRONTROWCREW_DB_USER", "betafrontrowcrew"),
            "PASSWORD": os.environ.get("BETAFRONTROWCREW_DB_PASSWORD", "betafrontrowcrew"),
            "HOST": os.environ.get("BETAFRONTROWCREW_DB_HOST", "localhost"),
            "PORT": os.environ.get("BETAFRONTROWCREW_DB_PORT", "5432"),
        }
    }

# Cache
if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.PyLibMCCache",
            "LOCATION": os.environ.get(
                "BETAFRONTROWCREW_MEMCACHED_SOCKET",
                "/tmp/memcached.sock"
            )
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATIC_URL = os.environ.get("BETAFRONTROWCREW_STATIC_URL", "/static/")
STATIC_ROOT = os.environ.get("BETAFRONTROWCREW_STATIC_ROOT", "/tmp/static/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Media files (User Uploads)
# https://docs.djangoproject.com/en/3.2/topics/files/

MEDIA_URL = os.environ.get("BETAFRONTROWCREW_MEDIA_URL", "/media/")
MEDIA_ROOT = os.environ.get("BETAFRONTROWCREW_MEDIA_ROOT", "/tmp/media/")

# Celery
CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_TASK_EAGER_PROPAGATES = DEBUG
CELERY_TASK_REMOTE_TRACEBACKS = DEBUG
CELERY_RESULT_BACKEND = "django-db"

if not DEBUG:
    celery_user = os.environ.get("BETAFRONTROWCREW_CELERY_USER", None)
    celery_password = os.environ.get("BETAFRONTROWCREW_CELERY_PASSWORD", None)
    celery_host = os.environ.get("BETAFRONTROWCREW_CELERY_HOST", "127.0.0.1")
    celery_port = os.environ.get("BETAFRONTROWCREW_CELERY_PORT", 5672)
    celery_vhost = os.environ.get("BETAFRONTROWCREW_CELERY_VHOST", None)
    if not any([var is None for var in (celery_user, celery_password, celery_vhost)]):
        CELERY_BROKER_URL = (
            f"amqp://{celery_user}"
            f":{celery_password}"
            f"@{celery_host}"
            f":{celery_port}"
            f"/{celery_vhost}"
        )

    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
