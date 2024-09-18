from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["0.0.0.0",'24.199.125.52',"*","24.144.68.190"]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# get_secret("SECRET_KEY")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #'ENGINE': 'django.db.backends.mysql',
        'NAME': get_secret("DB_NAME"),
        'USER': get_secret("USER"),
        'PASSWORD': get_secret("PASSWORD"),
        'HOST': 'localhost',
        'PORT': '5432'
    },
    'OPTIONS': {
     "init_command": "SET foreign_key_checks = 0;",
     },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR.child('static')]

STATIC_ROOT = BASE_DIR.child('staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')