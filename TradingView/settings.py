import os
from pathlib import Path
import pymysql
pymysql.install_as_MySQLdb()

# BASE_DIR is the base directory of your Django project
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!nq9x^t8v16n@9q+#v$zjw5z^ub2o@b0c_o0+%p+ix#o%nrbf5'

KEY= "SADFSyFSv-aD&WF9AWEgBLA1a323%423RB#JfVD@-2FeNEJtNVIER=EVER%n5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS - allow all hosts for development, restrict in production
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
'''CORS_ORIGIN_WHITELIST = (
  'http://localhost:8000',
)'''  
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# Custom user model
AUTH_USER_MODEL = 'accounts.User'  # Use CustomUser, not User


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'rest_framework',
    'rest_framework_simplejwt',
    'TradingView',
    
   
   
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    
]

ROOT_URLCONF = 'TradingView.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates', 
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

WSGI_APPLICATION = 'TradingView.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tradingview',
        'HOST':'aiinfox.cf4ysyasm9bi.ap-south-1.rds.amazonaws.com',
        'USER':'admin',
        'PASSWORD':'narakanar',
        'PORT':'3306'
    }
}

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

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'


STATICFILES_DIRS = [
    BASE_DIR / "static",
    "/var/www/static/",
]
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# If you are using the Django Admin interface, customize it here.
# Example for configuring the admin title, header, etc.
ADMIN_SITE_HEADER = 'TradingView Admin'
ADMIN_SITE_TITLE = 'TradingView Admin Dashboard'



# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your email provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ats789456123@gmail.com'  
EMAIL_HOST_PASSWORD = 'vxxv kwsa kekc qtnm '

