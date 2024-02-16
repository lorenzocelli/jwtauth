import django
import pytest
from django.conf import settings


def pytest_configure():

    settings.configure(
        DATABASES={
            'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'},
            'other': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'other'},
        },
        SECRET_KEY="abcd1234",
        MIDDLEWARE=(
            'jwtauth.middleware.AuthenticationMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            "rest_framework",
            "jwtauth",
            "tests.test_views",
        ),
        ROOT_URLCONF="tests.test_views.urls",
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'jwtauth.JwtAuthentication',
            ],
        }
    )

    django.setup()


@pytest.fixture
def user_a_password():
    return "abc12345#"


@pytest.fixture
def user_a(user_a_password):
    from django.contrib.auth.models import User
    user = User.objects.create_user("john", "lennon@thebeatles.com", user_a_password)
    return user
