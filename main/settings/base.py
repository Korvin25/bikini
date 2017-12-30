# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


ADMINS = (
    ('Valentin Glinskiy', 'v.valych@gmail.com'),
)

MANAGERS = ADMINS

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)

FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'), )

SECRET_KEY = '2N5asL3=923u41iW1v1wj-0nP1(#jqs6dd%radf62&*%@8jmip&'

DEBUG = False

ALLOWED_HOSTS = []
DEFAULT_SITENAME = 'localhost:8000'

SITE_ID = 1


# Application definition

INSTALLED_APPS = (
    # 'suit',
    'apps.content.suit_apps.SuitConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.postgres',

    'adminsortable2',
    'ckeditor',
    'colorfield',
    'crequest',
    'django_cleanup',
    'django_object_actions',
    'django_select2',
    'easy_thumbnails',
    'el_pagination',
    'embed_video',
    'filer',
    'modeltranslation',
    'mptt',
    'request',
    'rosetta',
    'salmonella',
    'sortedm2m',
    # 'tabbed_admin',
    'tinymce',
    'watermarker',

    'apps.core',
    'apps.geo',
    'apps.lk',
    'apps.settings',
    'apps.catalog',
    'apps.cart',
    'apps.content',
    # 'apps.contests',
    # 'apps.blog',
    'apps.banners',
    # 'apps.payments',
    # 'apps.mailings',
    # 'apps.feedback',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'request.middleware.RequestMiddleware',

    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'crequest.middleware.CrequestMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',

                # custom:
                'apps.cart.context_processors.cart',
                'apps.content.context_processors.content',
                'apps.settings.context_processors.settings',
            ],
            'debug': DEBUG,
       },
   },
]


AUTH_USER_MODEL = 'lk.Profile'

ROOT_URLCONF = 'main.urls'
WSGI_APPLICATION = 'main.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '...',
        'USER': '...',
        'PASSWORD': '...',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LANGUAGE_CODE = 'ru'
LANGUAGES = (
    ('ru', 'Русский'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('it', 'Italiano'),
    ('es', 'Español'),
)
LANGUAGES_DICT = dict(LANGUAGES)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'apps/lang/locale'),
)

MODELTRANSLATION_CUSTOM_FIELDS = ('RichTextField', 'RichTextUploadingField', 'HTMLField',)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('ru',), 'de': ('en', 'ru',), 'fr': ('en', 'ru',),
                                                           'it': ('en', 'ru',), 'es': ('en', 'ru',),}
# MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'
MODELTRANSLATION_AUTO_POPULATE = True
# MODELTRANSLATION_AUTO_POPULATE = 'required'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

EMAIL_HOST = 'smtp.qqq.com'
EMAIL_PORT = 0
EMAIL_HOST_USER = 'qqq'
EMAIL_HOST_PASSWORD = 'qqq'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'qqq <qqq@qqq.com>'


CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'forcePasteAsPlainText': True,
        'language': 'ru',
        'width': '100%',
        'toolbar': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll', '-', 'Scayt']},
            '/',
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Format', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'others', 'items': ['-']},
            {'name': 'about', 'items': ['About']},
       ],
        'format_tags': 'p;h2;h3',
        'removeDialogTabs': 'image:advanced;link:advanced',
        'image_previewText': '&nbsp',
   },
    'simple': {
        'forcePasteAsPlainText': True,
        'language': 'ru',
        'width': '100%',
        'height': '80%',
        'toolbar': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'paragraph', 'groups': ['list', 'blocks'],
             'items': ['NumberedList', 'BulletedList', '-', 'Blockquote']},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic']},
            {'name': 'links', 'items': ['Link']},
       ],
        'removeDialogTabs': 'image:advanced;link:advanced',
        'image_previewText': '&nbsp',
   },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'normal': {
            # [2015-11-23 08:07:35,431: INFO/tasks]
            # 'format': '%(levelname)s %(message)s'
            'format': '[%(asctime)s: %(levelname)s/%(module)s] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },
    'handlers': {
        'email_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/email.log'),
            'formatter': 'normal',
        },
        'requests_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/requests.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'emailz': {
            # 'handlers': ['email_log_file', 'mail_admins'],
            'handlers': ['email_log_file'],
            'level': 'INFO',
        },
        # 'django.request': {
        #     'handlers': ['requests_file', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'width': 900,
    'height': 300,
    # 'cleanup_on_startup': True,
    # 'custom_undo_redo_levels': 10,
}


# SUIT_CONFIG = {
#     'ADMIN_NAME': 'Bikinimini.ru',

#     'HEADER_DATE_FORMAT': 'l, d.m.Y',
#     'HEADER_TIME_FORMAT': 'H:i',

#     'CONFIRM_UNSAVED_CHANGES': False,

#     'MENU_EXCLUDE': ('auth', 'sites', 'djcelery', 'watermarker',),
#     'MENU_OPEN_FIRST_CHILD': True,
#     # 'MENU_ICONS': {
#     #     'settings': 'icon-cog',
#     #     'treenav': 'icon-list',
#     #     'geo': 'icon-map-marker',
#     #     'content': 'icon-pencil',
#     #     'lk': 'icon-user',
#     #     'ads': 'icon-warning-sign',
#     #     'vacancies': 'icon-briefcase',
#     #     'contests': 'icon-star',
#     #     'jobroom_production': 'icon-home',
#     #     'support': 'icon-info-sign',
#     #     'feedback': 'icon-comment',
#     #     'payments': 'icon-shopping-cart',
#     #     'user_messages': 'icon-envelope',
#     #     'search': 'icon-search',
#     # }
# }

# TABBED_ADMIN_USE_JQUERY_UI = True


ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_SHOW_AT_ADMIN_PANEL = False


THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_ALIASES = {
    '': {
        'homepage_cover': {'size': (1939, 937), 'crop': True, 'quality': 100},
        'homepage_girl': {'size': (737, 737), 'crop': False, 'upscale': True, 'quality': 100},

        'footer_banner': {'size': (1407, 408), 'crop': True, 'upscale': True, 'quality': 100},

        'attribute_option': {'size': (37, 37), 'crop': True, 'quality': 100, 'upscale': True},
        'attribute_option_detail': {'size': (46, 46), 'crop': True, 'quality': 100, 'upscale': True},
        'admin_attribute_option': {'size': (200, 200), 'crop': True, 'quality': 100, 'upscale': True},
        'product_style': {'size': (134, 134), 'crop': True, 'quality': 100, 'upscale': True},

        'product_cover': {'size': (220, 220), 'crop': True, 'quality': 100},
        'cart_product_cover': {'size': (86, 86), 'crop': True, 'quality': 100},

        'admin_product_photo': {'size': (140, 140), 'crop': True, 'quality': 100},
        'product_photo_preview': {'size': (387, 396), 'crop': True, 'quality': 100, 'upscale': True},
        'product_photo_thumb': {'size': (70, 70), 'crop': True, 'quality': 100, 'upscale': True},
        'product_photo_big': {'size': (1000, 1000), 'crop': False, 'quality': 100, 'upscale': True},

        'video_preview': {'size': (352, 183), 'crop': True, 'quality': 100, 'upscale': True},
    },
}


# https://django-request.readthedocs.io/en/latest/settings.html
REQUEST_IGNORE_AJAX = True
REQUEST_IGNORE_PATHS = (
    r'^admin/',
)


EL_PAGINATION_PER_PAGE = 15


WATERMARK_QUALITY = 100


# для редактирования стран
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1500
