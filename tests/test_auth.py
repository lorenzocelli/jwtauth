from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from rest_framework import status

from jwtauth.models import ActiveToken, BlacklistedToken
from jwtauth.settings import api_settings
from jwtauth.tokens import AccessToken, RefreshToken


def login(username, password):
    client = Client()
    response = client.post(
        reverse("login"),
        {"username": username, "password": password},
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(response.cookies) == 2

    client.cookies = response.cookies
    return client, response


@pytest.fixture
def logged_client(user_a, user_a_password):
    client, response = login(user_a.username, user_a_password)
    client.cookies = response.cookies
    return client


@pytest.mark.django_db
def test_login(user_a, user_a_password):
    client, response = login(user_a.username, user_a_password)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(response.cookies) == 2


@pytest.mark.django_db
@pytest.mark.parametrize("view", ["logged1", "logged2"])
def test_forged_tokens(client, view):
    client.cookies[api_settings.ACCESS_TOKEN_COOKIE_NAME] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxNDEsImlhdCI6MTcxNzMzNjc2OCwiZXhwIjoxN"
        "zE3MzM3MDY4fQ.Gl5K5xxGIwtYgklWy-3-jGHbOk_bjdCZmtzJbPJsmw8"
    )
    client.cookies[api_settings.REFRESH_TOKEN_COOKIE_NAME] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9zdHJpbmciOiJhQ3gwVlJUU083STBzTU1EWDRITnY2V"
        "DY5emR5TVYiLCJ1c2VyX2lkIjoxLCJpYXQiOjE3MTczMzY5MzYsImV4cCI6MTcxNzQyMzMzNn0.btM01q-P6UDHAkq"
        "hZvbkNsyrScDvwLSDKKezD7IJeFU"
    )
    response = client.get(reverse(view))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize("view", ["logged1", "logged2"])
def test_expired_tokens(client, user_a, view):
    # create valid but expired tokens for user_a
    access_token = AccessToken(from_user=user_a, duration=timedelta(0))  # zero seconds
    refresh_token = RefreshToken(from_user=user_a, duration=timedelta(0))  # zero seconds
    refresh_token.save()

    # set the cookies
    client.cookies[api_settings.ACCESS_TOKEN_COOKIE_NAME] = access_token.encoding
    client.cookies[api_settings.REFRESH_TOKEN_COOKIE_NAME] = refresh_token.encoding

    # verify the request to a logged view is forbidden
    response = client.get(reverse(view))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_protected_view_1(logged_client):
    response = logged_client.get(reverse("logged1"))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_protected_view_2(logged_client):
    response = logged_client.get(reverse("logged2"))
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_username_logged(logged_client, user_a):
    response = logged_client.get(reverse("username"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user_a.username


@pytest.mark.django_db
def test_username_not_logged(client):
    response = client.get(reverse("username"))
    assert response.status_code == 200
    assert response.data["username"] == ""


@pytest.mark.django_db
@pytest.mark.parametrize("view", ["logged1", "logged2"])
def test_forbidden_view(client, view):
    response = client.get(reverse(view))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_logout(logged_client):
    response = logged_client.delete(reverse("logout"))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    for cookie in response.cookies.values():
        # verify the cookie has been deleted
        assert cookie["max-age"] == 0

    # verify the active token has been removed
    assert ActiveToken.objects.count() == 0

    # verify the refresh token has been blacklisted
    assert BlacklistedToken.objects.count() == 1
