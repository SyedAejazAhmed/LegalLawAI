import os
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key-here")


# ✅ Best method (Automatically detects project path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_URLCONF = "needhi_backend.urls"  # ✅ Replace with your project's name

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "chatbot",  # ✅ Your chatbot app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "chatbot/templates")],  # ✅ Ensures chatbot templates work
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"  
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Change if needed
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "chatbot/static"),  # Change to match your actual path
]

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]  # ✅ Prevents deployment errors
DEBUG = True