from django.conf import settings

from jwtauth.settings import api_settings
from jwtauth.tokens import AccessToken, RefreshToken

ACCESS_TOKEN_KEY = api_settings.ACCESS_TOKEN_COOKIE_NAME
REFRESH_TOKEN_KEY = api_settings.REFRESH_TOKEN_COOKIE_NAME


class AuthManager:
    def __init__(self, request):
        self.access_token = get_access_token(request)
        self.refresh_token = get_refresh_token(request)
        self.silent_refresh = False
        self.is_authenticated = False
        self.logging_in = False
        self.logging_out = False
        self.user = None

        if not self.access_token or not self.refresh_token:
            # in order to be authenticated, the user must provide both the
            # authentication token (even if expired) and a valid refresh token
            return

        if not self.access_token.valid() or not self.refresh_token.valid():
            # we end up here if:
            # - one of the tokens was forged by a malicious user
            # - the refresh token was blacklisted
            return

        if self.access_token.expired():
            if self.refresh_token.expired():
                # both tokens are expired, the user has to log in again
                return

            # we silently refresh the authentication token and let the user in
            self.silent_refresh = True
            self.access_token = self.refresh_token.gen_access_token()

        # the authentication token is valid and not expired
        self.user = self.access_token.user
        self.is_authenticated = True

    def login(self, user) -> None:
        if not user:
            raise Exception("Please provide a valid user")

        if self.is_authenticated:  # already logged in
            raise Exception("User is already logged in")

        self.access_token = AccessToken(from_user=user)

        self.refresh_token = RefreshToken(from_user=user)
        self.refresh_token.save()

        self.logging_in = True
        self.is_authenticated = True
        self.user = user

    def logout(self) -> None:
        self.logging_out = True

    def apply(self, response) -> None:
        if self.silent_refresh:
            # we refresh and update the authentication token only
            set_access_token(response, self.refresh_token.gen_access_token())

        if self.logging_in:
            set_access_token(response, self.access_token)
            set_refresh_token(response, self.refresh_token)

        if self.logging_out:
            if self.refresh_token and self.refresh_token.valid() and not self.refresh_token.expired():
                # blacklist the token if valid and still alive
                self.refresh_token.blacklist()

            delete_access_token(response)
            delete_refresh_token(response)


def get_token(request, key, token_class):
    if key not in request.COOKIES:
        return None

    return token_class(from_encoding=request.COOKIES[key])


def set_token(response, key, token):
    secure = not settings.DEBUG  # locally, we allow non-secure cookies
    response.set_cookie(key, token.encoding, httponly=True, samesite="Strict", secure=secure)


def get_access_token(request):
    return get_token(request, ACCESS_TOKEN_KEY, AccessToken)


def get_refresh_token(request):
    return get_token(request, REFRESH_TOKEN_KEY, RefreshToken)


def set_access_token(response, token):
    set_token(response, ACCESS_TOKEN_KEY, token)


def set_refresh_token(response, token):
    set_token(response, REFRESH_TOKEN_KEY, token)


def delete_access_token(response):
    response.delete_cookie(ACCESS_TOKEN_KEY)


def delete_refresh_token(response):
    response.delete_cookie(REFRESH_TOKEN_KEY)
