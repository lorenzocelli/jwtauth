# jwtauth

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Test](https://github.com/lorenzocelli/jwtauth/actions/workflows/python-test.yml/badge.svg?branch=main)

A JWT-based authentication system for 
[Django REST Framework](https://github.com/encode/django-rest-framework/tree/master).

## Installation 🪄

This package is available on the [pip registry](https://pypi.org/project/drf-cookie-jwtauth/). 
To install it, you can run:
```
pip install drf-cookie-jwtauth
```

## Setup ⚙️

Add `jwtauth` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'jwtauth',
    # ...
]
```

Add `jwtauth.JwtAuthentication` to the REST framework list of authentication classes in your
settings file:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'jwtauth.JwtAuthentication',
        # ...
    ],
    # ...
}
```

Then, add `jwtauth.middleware.AuthenticationMiddleware` to the list of middleware classes:

```python
MIDDLEWARE = [
    'jwtauth.middleware.AuthenticationMiddleware',
    # ...
]
```

You can now run `python manage.py migrate` to create the models.

## Usage 📕

Use the `login` method to create a JWT token for the user and store it in the cookies, so that in the next requests
the user will be authenticated. For example:

```python
from jwtauth import login
from django.contrib.auth import authenticate


@api_view(['POST'])
def login_view(request):
    body = JSONParser().parse(request)

    # use an authentication backend to validate the credentials
    user = authenticate(
        username=body['username'],
        password=body['password']
    )

    if user is None:
        # credentials are not valid
        raise AuthenticationFailed('Invalid username or password.', 403)

    # login the user
    login(request, user)
    
    return Response(status=204)
```

To invalidate the tokens and logout the user, simply invoke the `logout` method, passing the request:

```python
from jwtauth import logout

@api_view(['DELETE'])
def logout_view(request):
    # logout the user
    logout(request)
    
    return Response(status=204)
```

To deny access to a resource when the user is logged out you can use REST framework's permissions.
You can then access the logged user through the `request.user` attribute.

```python
from rest_framework.permissions import IsAuthenticated


# function view with permission decorator: only accessible to logged users,
# otherwise a 403 Forbidden response is returned
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logged_view(request):
    user = request.user # logged user
    
    # ...
    
    return Response(status=204)
```

Equivalently, using class views:

```python
from rest_framework.permissions import IsAuthenticated


# class view with permission attribute
class LoggedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user # logged user
        
        # ...
        
        return Response(status=204)
```

You can also rely on the `is_authenticated` attribute to check if the user is logged in.
When the user is not logged in, `request.user` will be an instance of Django's `AnonymousUser`.

```python
@api_view(['GET'])
def my_view(request):

    if request.user.is_authenticated:
        # do something with the logged user
        # ...

    # user is not logged in
    # ...
```

## Additional settings

There are additional settings that you can change by adding a `JWTAUTH` dictionary to your
`settings.py` file. The following are all available settings with their default values:

```python
JWTAUTH = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ACCESS_TOKEN_COOKIE_NAME": "access_token",
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
}
```

Please note that when `SIGNING_KEY` is not set, Django's `SECRET_KEY` will be used.

## Limitations ⚠️

- This is a prototype, not ready to be used in production.
- Active tokens and blacklisted tokens are not automatically deleted from the database after they expire.
- Authentication through header `Authorization: Bearer` is not yet supported.
- Tokens are not encrypted in the database.
