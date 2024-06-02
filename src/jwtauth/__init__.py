from rest_framework import authentication, exceptions


class JwtAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):

        if request.jwtauth.is_authenticated:
            return request.jwtauth.user, None

        if request.jwtauth.access_token or request.jwtauth.refresh_token:
            # the user attempted to log in but using invalid or expired tokens
            raise exceptions.AuthenticationFailed("Tokens are either invalid or expired.")

        return None


def login(request, user):
    """Logs the user in and sets the access and refresh tokens."""
    request.jwtauth.login(user)


def logout(request):
    """Logs the user out and invalidates the access and refresh tokens."""
    request.jwtauth.logout()
