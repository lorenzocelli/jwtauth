from rest_framework import authentication, exceptions


class JwtAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        if request.jwtauth.is_authenticated:
            return request.jwtauth.user, None

        return None


def login(request, user):
    """Logs the user in and sets the access and refresh tokens."""
    request.jwtauth.login(user)


def logout(request):
    """Logs the user out and invalidates the access and refresh tokens."""
    request.jwtauth.logout()
