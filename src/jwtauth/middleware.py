from jwtauth.manager import AuthManager


class AuthenticationMiddleware:
    """jwtauth authentication middleware. Required for the package to work."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # set the manager as an attribute of the request
        request.jwtauth = AuthManager(request)

        # process the request
        response = self.get_response(request)

        # update the response cookies
        request.jwtauth.apply(response)

        return response
