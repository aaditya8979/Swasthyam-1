"""
Django settings for Swasthyam project.
Optimized for health data security and multi-language support.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-CHANGE-THIS-IN-PRODUCTION'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.vercel.app', 'now.sh', '127.0.0.1', 'localhost']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'django.contrib.humanize',  # For better date/number formatting
    
    # Local apps
    'main',
    'users',
    'maternal_health',
    'community_forum',
    'child_tracker',
    'health_calculators',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # For i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # For language switching
                'django.template.context_processors.media',  # For profile images
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# Replace the old SQLite DATABASES = { ... } block with this:

DATABASES = {
    'default': dj_database_url.config(
        # Replace this string with your actual Connection String from Step 1
        default='postgresql://neondb_owner:npg_uLvA2I3FGsSX@ep-floral-meadow-a10n9nee-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require', 
        conn_max_age=600
    )
}

# For production, use PostgreSQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'swasthyam_db',
#         'USER': 'your_db_user',
#         'PASSWORD': 'your_db_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication redirects
LOGIN_URL = 'users:auth'
LOGIN_REDIRECT_URL = 'main:dashboard'
LOGOUT_REDIRECT_URL = 'main:landing'

# Session security
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF security
CSRF_COOKIE_SECURE = False  # Set True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Message framework tags for Tailwind CSS
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'bg-gray-100 text-gray-800',
    messages.INFO: 'bg-blue-100 text-blue-800',
    messages.SUCCESS: 'bg-green-100 text-green-800',
    messages.WARNING: 'bg-yellow-100 text-yellow-800',
    messages.ERROR: 'bg-red-100 text-red-800',
}

# Email configuration (for password reset, notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# For production with Gmail:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'Swasthyam <noreply@swasthyam.com>'

# OpenAI API Configuration (for RAG Chatbot)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # Set in environment variables

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Allowed image formats for profile pictures
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'



MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
