# -*- coding: utf-8 -*-

# Django settings for te project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

#ADMINS = (
#    ('stclaus', 'stclaus@halogen-dg.com'),
#    ('alex', 'alex@halogen-dg.com'),
#)

#MANAGERS = ADMINS

#DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'tren'             # Or path to database file if using sqlite3.
#DATABASE_USER = 'tren'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'ait7Quoo'         # Not used with sqlite3.
#DATABASE_HOST = 'db'             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_nam
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
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

import os
SITE_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__)) + '/../') + '/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = SITE_ROOT+'tren/htdocs/'
#STATIC_ROOT = os.path.join(SITE_ROOT, 'gpsfun/htdocs/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(SITE_ROOT, 'gpsfun/data/')

HDG_MEDIA_ROOT=os.path.join(SITE_ROOT, 'DjHDGutils/htdocs/')
SCRIPTS_ROOT=os.path.join(SITE_ROOT, 'gpsfun/scripts/')


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, "gpsfun/htdocs/"),
    os.path.join(SITE_ROOT, "gpsfun/static/"),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/'
# ADMIN_MEDIA_PREFIX=os.path.join(MEDIA_URL, "admin/")
# Make this unique, and don't share it with anybody.
# SECRET_KEY='AeW9aisaup8ahGheTheix6Xexe3Vei3CAenai0oilaTh9juirech4OosZou2ahSi'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS=(
    'django.template.loaders.filesystem.Loader',
    # 'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)


MIDDLEWARE=(
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'userena.UserenaLocaleMiddleware',
    # 'gpsfun.main.views.MaintenanceMiddleware',
)

SECRET_KEY='AeW9aisaup8ahGheTheix6Xexe3Vei3CAenai0oilaTh9juirech4OosZou2ahSi'
CSSVERSION=4

ROOT_URLCONF='gpsfun.urls'

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
                # 'flashcross.context.global_context',
                # 'social_django.context_processors.backends',
                # 'social_django.context_processors.login_redirect',
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
    'gpsfun.DjHDGutils',
    'gpsfun.tableview',
    'gpsfun.main.GeoName',
    'gpsfun.main.GeoCachSU',
    'gpsfun.main.GeoMap',
    'gpsfun.main.GeoKrety',
    'gpsfun.main.User',
    'gpsfun.main.Carpathians',
    'gpsfun.gpsfun_admin',
    'gpsfun.main',
    'gpsfun.geocaching_su_stat',
    'gpsfun.geokret',
    'gpsfun.geoname',
    'gpsfun.map',
    'gpsfun.user',
    'gpsfun.carpathians',
    'django_registration',
    'profiles',
    'django_tables2',
    'django_filters',
    'crispy_forms',
)


DATE_FORMAT="d.m.Y"
TIME_FORMAT="H:i"

AUTH_PROFILE_MODULE='User.GPSFunUser'
ANONYMOUS_USER_ID=-1

# AUTH_PROFILE_MODULE = 'gpsfun.accounts.Profile'
AUTHENTICATION_BACKENDS=(
    #'gpsfun.auth_backends.CustomUserModelBackend',
    # 'userena.backends.UserenaAuthenticationBackend',
    # 'guardian.backends.ObjectPermissionBackend',
    # 'social_auth.backends.twitter.TwitterBackend',
    # 'social_auth.backends.facebook.FacebookBackend',
    # 'social_auth.backends.google.GoogleOAuthBackend',
    # 'social_auth.backends.google.GoogleOAuth2Backend',
    # 'social_auth.backends.google.GoogleBackend',
    # 'social_auth.backends.yahoo.YahooBackend',
    # 'social_auth.backends.browserid.BrowserIDBackend',
    # 'social_auth.backends.contrib.linkedin.LinkedinBackend',
    # 'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    # 'social_auth.backends.contrib.orkut.OrkutBackend',
    # 'social_auth.backends.contrib.foursquare.FoursquareBackend',
    # 'social_auth.backends.contrib.github.GithubBackend',
    # 'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    # 'social_auth.backends.contrib.live.LiveBackend',
    # 'social_auth.backends.contrib.skyrock.SkyrockBackend',
    # 'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    # 'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CUSTOM_USER_MODEL='User.GPSFunUser'

ACCOUNT_ACTIVATION_DAYS=2
# LAST_CONFIRM_DAYS = 2

# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

EMAIL_USE_TLS=True
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='gpsfun.info@gmail.com'
EMAIL_HOST_PASSWORD='utjrtibyuUTJRTIBYU'

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL='info@google.ru'

# EMAIL_HOST = 'mail.halogen.kharkov.ua'
# EMAIL_HOST_USER = 'testuser@halogen.kharkov.ua'
# EMAIL_HOST_PASSWORD = 'Ohl5weig'
# EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL='gpsfun.info@gmail.com'



# LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL='/'
LOGIN_URL='/accounts/login/'
LOGOUT_URL='/accounts/logout/'
LOGIN_ERROR_URL='/accounts/login/error/'

# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/accounts/new/users/redirect/'
# SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
# SOCIAL_AUTH_BACKEND_ERROR_URL = '/new-error-url/'
# SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
# SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
# SOCIAL_AUTH_UUID_LENGTH = 16
# SOCIAL_AUTH_EXTRA_DATA = False
# SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email',]
# SOCIAL_AUTH_EXPIRATION = 'expires'

TEMPLATE_CONTEXT_PROCESSORS=(
    # "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    'django.contrib.auth.context_processors.auth',
    # 'social_auth.context_processors.social_auth_by_name_backends',
    # 'social_auth.context_processors.social_auth_backends',
    # 'social_auth.context_processors.social_auth_by_type_backends',
    # 'social_auth.context_processors.social_auth_login_redirect',
    "gpsfun.main.Utils.context.template",
    # 'pybb.context_processors.processor',
    # "allauth.account.context_processors.account",
    # "allauth.socialaccount.context_processors.socialaccount",
)

ROW_PER_PAGE=100

TWITTER_CONSUMER_KEY=''
TWITTER_CONSUMER_SECRET=''
FACEBOOK_APP_ID=''
FACEBOOK_API_SECRET=''
LINKEDIN_CONSUMER_KEY=''
LINKEDIN_CONSUMER_SECRET=''
ORKUT_CONSUMER_KEY=''
ORKUT_CONSUMER_SECRET=''
GOOGLE_CONSUMER_KEY=''
GOOGLE_CONSUMER_SECRET=''
GOOGLE_OAUTH2_CLIENT_ID=''
GOOGLE_OAUTH2_CLIENT_SECRET=''
FOURSQUARE_CONSUMER_KEY=''
FOURSQUARE_CONSUMER_SECRET=''
VK_APP_ID=''
VK_API_SECRET=''
LIVE_CLIENT_ID=''
LIVE_CLIENT_SECRET=''
SKYROCK_CONSUMER_KEY=''
SKYROCK_CONSUMER_SECRET=''
YAHOO_CONSUMER_KEY=''
YAHOO_CONSUMER_SECRET=''

LOCALE_PATHS=(SITE_ROOT + 'gpsfun/locale/',)

MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'



DATE_FORMAT="d.m.Y"
TIME_FORMAT="H:i"

AUTH_PROFILE_MODULE='User.GPSFunUser'
ANONYMOUS_USER_ID=-1

# AUTH_PROFILE_MODULE = 'gpsfun.accounts.Profile'
AUTHENTICATION_BACKENDS=(
    #'gpsfun.auth_backends.CustomUserModelBackend',
    # 'userena.backends.UserenaAuthenticationBackend',
    # 'guardian.backends.ObjectPermissionBackend',
    # 'social_auth.backends.twitter.TwitterBackend',
    # 'social_auth.backends.facebook.FacebookBackend',
    # 'social_auth.backends.google.GoogleOAuthBackend',
    # 'social_auth.backends.google.GoogleOAuth2Backend',
    # 'social_auth.backends.google.GoogleBackend',
    # 'social_auth.backends.yahoo.YahooBackend',
    # 'social_auth.backends.browserid.BrowserIDBackend',
    # 'social_auth.backends.contrib.linkedin.LinkedinBackend',
    # 'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    # 'social_auth.backends.contrib.orkut.OrkutBackend',
    # 'social_auth.backends.contrib.foursquare.FoursquareBackend',
    # 'social_auth.backends.contrib.github.GithubBackend',
    # 'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    # 'social_auth.backends.contrib.live.LiveBackend',
    # 'social_auth.backends.contrib.skyrock.SkyrockBackend',
    # 'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    # 'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CUSTOM_USER_MODEL='User.GPSFunUser'

ACCOUNT_ACTIVATION_DAYS=2
# LAST_CONFIRM_DAYS = 2

# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

EMAIL_USE_TLS=True
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='gpsfun.info@gmail.com'
EMAIL_HOST_PASSWORD='utjrtibyuUTJRTIBYU'

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL='info@google.ru'

# EMAIL_HOST = 'mail.halogen.kharkov.ua'
# EMAIL_HOST_USER = 'testuser@halogen.kharkov.ua'
# EMAIL_HOST_PASSWORD = 'Ohl5weig'
# EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL='gpsfun.info@gmail.com'



# LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL='/'
LOGIN_URL='/accounts/login/'
LOGOUT_URL='/accounts/logout/'
LOGIN_ERROR_URL='/accounts/login/error/'

# SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/accounts/new/users/redirect/'
# SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/account-disconnected-redirect-url/'
# SOCIAL_AUTH_BACKEND_ERROR_URL = '/new-error-url/'
# SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
# SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

# SOCIAL_AUTH_DEFAULT_USERNAME = 'new_social_auth_user'
# SOCIAL_AUTH_UUID_LENGTH = 16
# SOCIAL_AUTH_EXTRA_DATA = False
# SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email',]
# SOCIAL_AUTH_EXPIRATION = 'expires'

TEMPLATE_CONTEXT_PROCESSORS=(
    # "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    'django.contrib.auth.context_processors.auth',
    # 'social_auth.context_processors.social_auth_by_name_backends',
    # 'social_auth.context_processors.social_auth_backends',
    # 'social_auth.context_processors.social_auth_by_type_backends',
    # 'social_auth.context_processors.social_auth_login_redirect',
    "gpsfun.main.Utils.context.template",
    # 'pybb.context_processors.processor',
    # "allauth.account.context_processors.account",
    # "allauth.socialaccount.context_processors.socialaccount",
)

ROW_PER_PAGE=100

TWITTER_CONSUMER_KEY=''
TWITTER_CONSUMER_SECRET=''
FACEBOOK_APP_ID=''
FACEBOOK_API_SECRET=''
LINKEDIN_CONSUMER_KEY=''
LINKEDIN_CONSUMER_SECRET=''
ORKUT_CONSUMER_KEY=''
ORKUT_CONSUMER_SECRET=''
GOOGLE_CONSUMER_KEY=''
GOOGLE_CONSUMER_SECRET=''
GOOGLE_OAUTH2_CLIENT_ID=''
GOOGLE_OAUTH2_CLIENT_SECRET=''
FOURSQUARE_CONSUMER_KEY=''
FOURSQUARE_CONSUMER_SECRET=''
VK_APP_ID=''
VK_API_SECRET=''
LIVE_CLIENT_ID=''
LIVE_CLIENT_SECRET=''
SKYROCK_CONSUMER_KEY=''
SKYROCK_CONSUMER_SECRET=''
YAHOO_CONSUMER_KEY=''
YAHOO_CONSUMER_SECRET=''

LOCALE_PATHS = (SITE_ROOT + 'gpsfun/locale/',)

MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'

# STATICFILES_DIRS=[]

PYBB_TEMPLATE='base_bootstrap.html'
try:
    from gpsfun.custom_settings import *
except ImportError:
    pass

