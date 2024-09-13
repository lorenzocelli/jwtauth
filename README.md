# jwtauth

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Test](https://github.com/lorenzocelli/jwtauth/actions/workflows/python-test.yml/badge.svg?branch=main)

A JWT-based authentication system for 
[Django REST Framework](https://github.com/encode/django-rest-framework/tree/master).

## 🪄 Installation

This package is available on the [pip registry](https://pypi.org/project/drf-cookie-jwtauth/). 
To install it, you can run:
```
pip install drf-cookie-jwtauth
```

## ⚙️ Configuration

Add `jwtauth` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'jwtauth',
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

## 📕 Usage

Use the `login` method to create a JWT token for the user and store it in the cookies, so that in the next requests
the user will be authenticated. For example:

```python
from jwtauth import login


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

To check if a user is logged in, you can use REST framework's permissions:

```python
from rest_framework.permissions import IsAuthenticated


# function view with permission decorator
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logged_view(request):
    # only for logged users, otherwise a 403 Forbidden response is returned
    return Response(status=204)
```

Equivalently, using class views:

```python
from rest_framework.permissions import IsAuthenticated


# class view with permission attribute
class LoggedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # only for logged users, otherwise a 403 Forbidden response is returned
        return Response(status=204)
```

You can also rely on the `request.user` attribute to access the logged user (or Django's `AnonymousUser` if the user is
not logged in):

```python
@api_view(['GET'])
def my_view(request):

    if request.user.is_authenticated:
        # do something with the logged user
        # ...

    # user is not logged in
    # ...
```

## 🚫 Limitations

- This is a prototype, not ready to be used in production.
- Active tokens and blacklisted tokens are not automatically deleted from the database after they expire.
- Authentication through header `Authorization: Bearer` is not yet supported.
- Tokens are not encrypted in the database.
