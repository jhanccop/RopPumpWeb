import secrets
from django.core.exceptions import ImproperlyConfigured
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from unipath import Path
#BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path(__file__).ancestor(3)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

with open("secret.json") as f:
    secret = json.loads(f.read())

def get_secret(secret_name, secrets = secret):
    try:
        return secrets[secret_name]
    except:
        msg = "variable %s unknow" % secret_name
        raise ImproperlyConfigured(msg)

SECRET_KEY = get_secret("SECRET_KEY")

# Application definition|

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # local apps
    'Apps.batteries',
    'Apps.company',
    'Apps.data',
    'Apps.device',
    'Apps.equipment',
    'Apps.field',
    'Apps.groups',
    'Apps.home',
    #'Apps.input',
    #'Apps.overview',
    #'Apps.production',
    #'Apps.settings',
    #'Apps.tests',
    'Apps.users',
    #'Apps.wells',
    #'Apps.wellServices',
    
    # third apps
    'multiselectfield'
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

ROOT_URLCONF = 'RopPumpWeb.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates')],
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

WSGI_APPLICATION = 'RopPumpWeb.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = False

USE_TZ = False

