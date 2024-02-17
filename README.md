# jwtauth

A JWT-based authentication system for 
[Django REST Framework](https://github.com/encode/django-rest-framework/tree/master).

## 🪄 Installation

This package is not available on the pip registry yet. To install it, download the compressed package from
[here](https://github.com/lorenzocelli/jwtauth/actions/runs/7941362543/artifacts/1253381430), 
extract it and then run:
```
python3 -m pip install jwtauth-0.0.1.tar.gz
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
from django.contrib.auth import authenticate

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

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

    login(request, user)
    return Response(status=204)
```

To invalidate the tokens and logout the user, simply invoke the `logout` method, passing the request:

```python
from jwtauth import logout

@api_view(['DELETE'])
def logout_view(request):
    logout(request)
    return Response(status=204)
```

## 🚫 Limitations

- This is a prototype, not ready to be used in production.
- Active tokens and refresh tokens are not deleted from the database after they expire.
- Authentication through header `Authorization: Bearer` is not yet supported.
