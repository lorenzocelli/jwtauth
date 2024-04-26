from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "JWTAUTH", None)

DEFAULTS = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ACCESS_TOKEN_COOKIE_NAME": "access_token",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
}

api_settings = APISettings(USER_SETTINGS, DEFAULTS, ())


def reload_api_settings(**kwargs) -> None:
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "JWTAUTH":
        api_settings = APISettings(value, DEFAULTS, ())


setting_changed.connect(reload_api_settings)
