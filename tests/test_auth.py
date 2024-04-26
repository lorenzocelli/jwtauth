import pytest
from django.urls import reverse
from django.test import Client
from jwtauth.models import ActiveToken, BlacklistedToken


def login(username, password):
    client = Client()
    response = client.post(
        reverse("login"),
        {"username": username, "password": password},
        content_type="application/json",
    )

    assert response.status_code == 204
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

    assert response.status_code == 204
    assert len(response.cookies) == 2


@pytest.mark.django_db
def test_protected_view_1(logged_client):
    response = logged_client.get(reverse("logged1"))
    assert response.status_code == 204


@pytest.mark.django_db
def test_protected_view_2(logged_client):
    response = logged_client.get(reverse("logged2"))
    assert response.status_code == 204


@pytest.mark.django_db
def test_username_logged(logged_client, user_a):
    response = logged_client.get(reverse("username"))
    assert response.status_code == 200
    assert response.data["username"] == user_a.username


@pytest.mark.django_db
def test_username_not_logged(client):
    response = client.get(reverse("username"))
    assert response.status_code == 200
    assert response.data["username"] == ""


@pytest.mark.django_db
def test_logout(logged_client):
    response = logged_client.delete(reverse("logout"))
    assert response.status_code == 204

    for cookie in response.cookies.values():
        # verify the cookie has been deleted
        assert cookie["max-age"] == 0

    # verify the active token has been removed
    assert ActiveToken.objects.count() == 0

    # verify the refresh token has been blacklisted
    assert BlacklistedToken.objects.count() == 1
