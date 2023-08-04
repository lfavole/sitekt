"""
Django settings for cate project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import sys
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.functional import lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR.parent / "scripts"))
from utils import App

settings = App(BASE_DIR.name).settings

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings.SECRET_KEY or "+jt!%+%erdp^y7h37v#68x31+u9ut6^8zryj@#zmu5p$_!u2)u"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings.DEBUG

if not DEBUG:
	CSRF_COOKIE_SECURE = True
	SESSION_COOKIE_SECURE = True
	CONN_MAX_AGE = 600
	ALLOWED_HOSTS = [settings.HOST]
	SECURE_SSL_REDIRECT = True
else:
	ALLOWED_HOSTS = ["*"]

GITHUB_WEBHOOK_KEY = settings.GITHUB_WEBHOOK_KEY

# Application definition

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.admindocs",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"adminsortable2",
	"betterforms",
	"easy_thumbnails",
	"tinymce",
	"cate",
	"users",
	"storage",
	"tracking",
	"aumonerie",
	"common",
	"errors",
	"espacecate",
	"calendrier_avent_2022",
	"django_cleanup", # must be placed last
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.middleware.gzip.GZipMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.http.ConditionalGetMiddleware",
	"cate.middleware.SpacelessMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
	"tracking.middleware.VisitorTrackingMiddleware",
]

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ROOT_URLCONF = "cate.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
				"cate.context_processors.app_name",
				"cate.context_processors.navbar_processor",
				"cate.context_processors.now_variable",
			],
		},
	},
]

WSGI_APPLICATION = "cate.wsgi.application"

TRACK_IGNORE_URLS = (
	r"^(favicon\.ico|robots\.txt)$",
	r"^admin/",
)

TRACK_IGNORE_STATUS_CODES = (403, 404, 500)

TRACK_PAGEVIEWS = True


STORAGES = {
    "default": {
        "BACKEND": "storage.storages.CustomFileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": BASE_DIR / "db.sqlite3",
	}
} if settings.USE_SQLITE else {
	"default": {
		"ENGINE": "django.db.backends.mysql",
		"NAME": settings.DB_NAME,
		"USER": settings.DB_USER,
		"PASSWORD": settings.DB_PASSWORD,
		"HOST": settings.DB_HOST,
		"OPTIONS": {
			"charset": "utf8mb4",
			"init_command": "SET sql_mode=\"STRICT_TRANS_TABLES\"",
		},
	}
}

AUTH_USER_MODEL = "users.User"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
	},
    {
	    "NAME": "cate.password_validation.PwnedPasswordValidator",
	},
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr-FR"

TIME_ZONE = "Europe/Paris"

USE_I18N = True
USE_L10N = True
LOCALE_PATHS = [BASE_DIR / "locale"]

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "src/"]
STATIC_ROOT = BASE_DIR / "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"

PRIVATE_MEDIA_URL = "private/"
PRIVATE_MEDIA_ROOT = BASE_DIR / "private/"

THUMBNAIL_BASEDIR = "thumbs"


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# TinyMCE editor


def add_url(text, url):
	return text % url


add_url_lazy = lazy(add_url)
static_lazy = lazy(static)
TINYMCE_JS_URL = STATIC_URL + "vendor/tinymce/tinymce.min.js" if settings.OFFLINE else "https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js"
TINYMCE_EXTRA_MEDIA = {
	"css": {
		"all": (
			"/static/tinymce/tinymce.css",
		)
	},
	"js": (
		"/static/tinymce/tinymce.js",
	)
}
TINYMCE_DEFAULT_CONFIG = {
	"language": "fr",
	"language_url": static_lazy("tinymce/langs/fr_FR.js"),
	"content_css": [
		"https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;1,400;1,700&display=swap",
		static_lazy("global/global.css"),
	],
	"content_style": "body{padding:8px}",
	"promotion": False,
	"plugins": "autolink code fullscreen help image link lists media preview quickbars save searchreplace table",
	"toolbar": (
		"undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
		"aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor removeformat | "
		"image media link"
	),
	"relative_urls": False,
	"image_advtab": True,
	"images_reuse_filename": True,
	"images_upload_credentials": True,
	# pylint: disable=C0209
	"images_upload_handler": add_url_lazy("""\
(blobInfo, progress) => new Promise((success, failure) => {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "%s");
	xhr.withCredentials = true;
	xhr.upload.onprogress = e => {
		progress(e.loaded / e.total * 100);
	};
	xhr.onerror = () => {
		failure("Image upload failed due to a XHR Transport error. Code: " + xhr.status);
	};
	xhr.onload = () => {
		if(xhr.status < 200 || xhr.status >= 300) {
			failure("HTTP Error: " + xhr.status);
			return;
		}
		var json = JSON.parse(xhr.responseText);
		if(!json || !json.location) {
			failure("Invalid JSON: " + xhr.responseText);
			return;
		}
		success(json.location);
	};
	var formData = new FormData();
	formData.append("file", blobInfo.blob(), blobInfo.filename());
	formData.append("csrfmiddlewaretoken", django.jQuery("#content-main form").get(0).csrfmiddlewaretoken.value);
	xhr.send(formData);
})
""", reverse_lazy("tinymce-upload-image")),
}
