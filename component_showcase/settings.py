import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-component-showcase-demo-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() not in ('false', '0', 'no')
_allowed = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
_pod_ip = os.environ.get('POD_IP', '')
ALLOWED_HOSTS = [h.strip() for h in _allowed if h.strip()] + ([_pod_ip] if _pod_ip else [])

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://components.djust.org').split(',')
    if origin.strip()
]

INSTALLED_APPS = [
    'daphne',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'channels',
    'djust',
    'djust_theming',
    'djust_components',
    'components',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'component_showcase.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'djust_theming.context_processors.theme_context',
                'djust_components.gallery.context_processors.gallery_theme',
            ],
        },
    },
]

ASGI_APPLICATION = 'component_showcase.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SILENCED_SYSTEM_CHECKS = [
    'djust.S001', 'djust.S005', 'djust.T010', 'djust.T011', 'djust.T012',
    'djust_theming.W001',  # upstream preset contrast warnings
]

LIVEVIEW_CONFIG = {
    'use_websocket': True,
    'debug_vdom': False,
}
