# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, '/home/tim/djbook')
sys.path.insert(0, '/home/tim/djbook/apps')

PROJECT_PATH = os.path.normpath('/home/tim/djbook/')

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
   ('Sobolev Andrey', 'mail.asobolev@yandex.ru'),
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'djbook',                      
        'USER': 'user',                       
        'PASSWORD': '',                 
        'HOST': '',                           
        'PORT': '', 
        'OPTIONS':  {'init_command': 'SET table_type=INNODB;', 'charset': 'utf8'},                          
    }
}


DEFAULT_CHARSET = 'utf-8'

SITE_ID = 1


MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media'

STATIC_URL = '/static'


SECRET_KEY = 'asdkjgaddfalasfgasfgasd1232sfdfsdf3'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (   
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'templates/gbook/locale'),
)

USE_I18N = True
USE_L10N = True

TIME_ZONE = 'Europe/Moscow'

#LANGUAGE_CODE = 'en-EN'
#LANGUAGE_CODE = 'ru-RU' # Choose your language

_ = lambda s: s
LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'djbook',
    'gbook',
    'captcha',
    'pagination',  
)

CAPTCHA_LENGTH = 5
CAPTCHA_FONT_SIZE = 24

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False



##############################################################
# DJANGO GUESTBOOK SETTINGS ################################## 

# new administrator create       
#python manage.py createsuperuser --username=joe 

GBOOK_EMAIL_FROM = 'noreply@yourhost.com' # administrator email


GBOOK_SECTIONS = (
    (u'Main', _(u'Main')),
    (u'Developing', _(u'Developing news')),
    (u'Testing', _(u'Testing')),
)

GBOOK_REGISTRATION_VIA_EMAIL = 'yes'  # yes/no

# By default new users are registered in two ways: 
# 1) Through email, by acknowledgement of the account. 
#     The given way of registration is bad that,
#     that everybody can be registered, without the 
#     knowledge of the administrator.
# 2) New user can add answers as not registered user and to 
#     ask acknowledgement of the registration by pressing 
#     to "Need registration", at answer addition.
#     In that case registration is carried out by the manager 
#     through an option "Messages from not registered users",
#     this way is better that the manager 
#     PRECISELY knows whom it has added. 
#     By default both ways of registration are accessible 
#     to new users, however you can 
#     to specify REGISTRATION_VIA_EMAIL = 'no', for this purpose 
#     that registration would be carried out only by you
#     through an option "Messages from not registered users".

 


