"""
Django settings for te project.
"""

import os
from dotenv import load_dotenv

load_dotenv()


DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

SITE_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__)) + '/../') + '/'

# Absolute path to the directory that holds media.
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'gpsfun/data/')

HDG_MEDIA_ROOT = os.path.join(SITE_ROOT, 'DjHDGutils/htdocs/')
SCRIPTS_ROOT = os.path.join(SITE_ROOT, 'gpsfun/scripts/')


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "gpsfun/htdocs/"),
    os.path.join(SITE_ROOT, "gpsfun/static/"),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    # 'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.load_template_source',
)


MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'gpsfun.main.views.MaintenanceMiddleware',
)

SECRET_KEY = os.environ['SECRET_KEY']

ROOT_URLCONF = 'gpsfun.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SITE_ROOT, 'gpsfun/templates/'),
                 os.path.join(SITE_ROOT, 'gpsfun/templates/admin/'),
                 ],
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

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap-responsive.html"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    # 'gpsfun.DjHDGutils',
    'gpsfun.tableview',
    'gpsfun.main.GeoName',
    'gpsfun.main.GeoCachSU',
    'gpsfun.main.GeoMap',
    'gpsfun.main.GeoKrety',
    'gpsfun.main.User',
    # 'gpsfun.main.Carpathians',
    'gpsfun.gpsfun_admin',
    'gpsfun.main',
    'gpsfun.geocaching_su_stat',
    'gpsfun.geokret',
    # 'gpsfun.geoname',
    'gpsfun.map',
    'gpsfun.user',
    'django_registration',
    'profiles',
    'django_tables2',
    'django_filters',
    'crispy_forms',
)
os.environ['SECRET_KEY']
DATABASE_ENGINE = 'mysql'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.environ['DATABASE_NAME']
DATABASE_USER = os.environ['DATABASE_USER']
DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']
DATABASE_PORT = os.environ['DATABASE_PORT']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    }
}

DATE_FORMAT = "d.m.Y"
TIME_FORMAT = "H:i"

AUTH_PROFILE_MODULE = 'User.GPSFunUser'
ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
CUSTOM_USER_MODEL = 'User.GPSFunUser'

ACCOUNT_ACTIVATION_DAYS = 2

EMAIL_USE_TLS = True
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = int(os.environ['EMAIL_PORT'])
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']

DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_ERROR_URL = '/accounts/login/error/'

TEMPLATE_CONTEXT_PROCESSORS = (
    # "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    'django.contrib.auth.context_processors.auth',
    "gpsfun.main.Utils.context.template",
)
ROW_PER_PAGE = 100

LOCALE_PATHS = (SITE_ROOT + 'gpsfun/locale/',)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


DATE_FORMAT = "d.m.Y"
TIME_FORMAT = "H:i"

AUTH_PROFILE_MODULE = 'User.GPSFunUser'
ANONYMOUS_USER_ID = -1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

CUSTOM_USER_MODEL = 'User.GPSFunUser'

ACCOUNT_ACTIVATION_DAYS = 2

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'gpsfun.info@gmail.com'
# EMAIL_HOST_PASSWORD = 'utjrtibyuUTJRTIBYU'
#
# DEFAULT_FROM_EMAIL = 'gpsfun.info@gmail.com'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_ERROR_URL = '/accounts/login/error/'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    'django.contrib.auth.context_processors.auth',
    "gpsfun.main.Utils.context.template",
)

ROW_PER_PAGE = 100

LOCALE_PATHS = (SITE_ROOT + 'gpsfun/locale/',)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

PYBB_TEMPLATE = 'base_bootstrap.html'
# try:
#     from gpsfun.custom_settings import *
# except ImportError:
#     pass
