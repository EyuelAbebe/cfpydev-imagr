"""
Django settings for imagr_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from configurations import Configuration

class base_settings (Configuration):

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = os.environ['SECRET_KEY']
    AUTH_USER_MODEL = 'imagr_user.ImagrUser'
    ROOT_URLCONF = 'imagr_site.urls'
    AUTH_USER_MODEL = 'imagr_user.ImagrUser'


    WSGI_APPLICATION = 'imagr_site.wsgi.application'
    
    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Application definition

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'south',
        'sorl.thumbnail',
        'imagr_images',
        'imagr_user',
        'gunicorn',
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )


    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = '../imagr_images/uploaded_images'
    MEDIA_URL = '/media/'

    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )

    THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'
    THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.pil_engine.Engine'
    THUMBNAIL_CACHE = 'default'
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': '/var/tmp/django_cache',
        }
    }

# first run prev confs then call class Dev

class Dev(base_settings):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    THUMBNAIL_DEBUG = DEBUG
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'imagr',
        }
    }


class Prod(base_settings):
    ALLOWED_HOSTS = ['http://ec2-54-191-166-39.us-west-2.compute.amazonaws.com',
                     'www.ec2-54-191-166-39.us-west-2.compute.amazonaws.com',
                     'ec2-54-191-166-39.us-west-2.compute.amazonaws.com']
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'imagr',
            'HOST': 'imagrdb.cj9whh42swi2.us-west-2.rds.amazonaws.com',
            'PORT': 5432,
        }
    }
