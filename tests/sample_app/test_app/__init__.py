import os

from jwtauth.settings import api_settings


for key in ["SIGNING_KEY", "ACCESS_TOKEN_COOKIE_NAME", "REFRESH_TOKEN_COOKIE_NAME", "ALGORITHM"]:
    env_value = os.getenv(key)
    print(f"{key}: {env_value}")

    if (value := getattr(api_settings, key)) != env_value:
        raise Exception(f"Unexpected setting value for key '{key}': {value}")
