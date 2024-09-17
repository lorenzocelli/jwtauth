from rest_framework import authentication


class JwtAuthentication(authentication.BaseAuthentication):
    """
    Authentication class for jwtauth package, to be added to DEFAULT_AUTHENTICATION_CLASSES.
    """

    def authenticate(self, request):
        if request.jwtauth.is_authenticated:
            return request.jwtauth.user, None

        return None


def login(request, user):
    """
    Logs the user in and sets the access and refresh tokens.
    After invoking this method the request will contain the logged user and request.is_authenticated
    will be true.
    """
    request.jwtauth.login(user)


def logout(request) -> None:
    """
    Logs the user out and invalidates the access and refresh tokens.
    Please note that this method does not take effect immediately but rather when the response is
    processed, therefore the request will still contain the current user and is_authenticated will
    still be true. The user will be logged out upon crafting the response.
    """
    request.jwtauth.logout()
