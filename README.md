# jwtauth

A JWT-based authentication system for 
[Django REST Framework](https://github.com/encode/django-rest-framework/tree/master).

## Installation

WIP

## Configuration

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

## Usage

WIP
