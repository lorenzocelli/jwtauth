from jwtauth.tokens import Token, UserToken, AccessToken, RefreshToken
from datetime import timedelta, datetime, timezone
from jwtauth.settings import api_settings
from jwtauth.models import ActiveToken
import pytest
import jwt


def test_valid_token():
    # create a token and verify it is marked as valid and not expired
    token = Token(from_data={"data": 42}, duration=timedelta(minutes=5))
    assert token.valid()
    assert not token.expired()


def test_token_decode():
    # create a token, encode it, decode it and verify it is marked as valid and not expired
    token_data = {"data": 42}
    original = Token(from_data=token_data, duration=timedelta(minutes=5))
    decoded = Token(from_encoding=original.encoding)
    assert decoded.valid()
    assert not decoded.expired()
    assert decoded.data == token_data


def test_token_expired():
    # create a token with a duration of 0 seconds and verify it is marked as expired
    token = Token(from_data={"data": 42}, duration=timedelta())
    assert token.expired()


def test_token_no_exp():
    # try decoding a token without an 'exp' claim and verify it is marked as invalid
    encoding = jwt.encode(
        {"data": 42, "iat": datetime.now(tz=timezone.utc)},
        api_settings.SIGNING_KEY,
        algorithm=api_settings.ALGORITHM,
    )
    token = Token(from_encoding=encoding)
    assert not token.valid()


def test_token_no_iat():
    # try decoding a token without a 'iat' claim and verify it is marked as invalid
    encoding = jwt.encode(
        {"data": 42, "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5)},
        api_settings.SIGNING_KEY,
        algorithm=api_settings.ALGORITHM,
    )
    token = Token(from_encoding=encoding)
    assert not token.valid()


def test_token_decode_expired():
    # create a token with a duration of 0 seconds, encode it, decode it
    # and verify it is marked as expired
    encoded = Token(from_data={"data": 42}, duration=timedelta())
    decoded = Token(from_encoding=encoded.encoding)
    assert decoded.expired()


def test_bad_token():
    # try to decode random data and verify the token is marked as invalid
    decoded = Token(from_encoding="12345")
    assert not decoded.valid()


def test_invalid_signature():
    # try to decode a token with an invalid signature and verify it is marked as invalid
    original = Token(from_data={"data": 42}, duration=timedelta(minutes=5))
    encoding = jwt.encode(original.jwt_data, "new_key", algorithm="HS256")
    malicious = Token(from_encoding=encoding)
    assert not malicious.valid()


def test_alg_none():
    # try to decode a malicious token with algorithm 'none' and verify it is marked as invalid
    original = Token(from_data={"data": 42}, duration=timedelta(minutes=5))
    encoding = jwt.encode(original.jwt_data, None, algorithm="none")
    malicious = Token(from_encoding=encoding)
    assert not malicious.valid()


@pytest.mark.django_db
def test_access_token(user_a):
    # create an access token and verify it is marked as valid and not expired
    token = AccessToken(from_user=user_a)
    assert token.valid()
    assert not token.expired()


@pytest.mark.django_db
def test_decode_access_token(user_a):
    # create an access token, encode it, decode it and verify it is marked as valid and not expired
    token = AccessToken(from_user=user_a)
    decoded = AccessToken(from_encoding=token.encoding)
    assert decoded.valid()
    assert not decoded.expired()
    assert decoded.user.id == user_a.id
    assert decoded.user.username == user_a.username


@pytest.mark.django_db
def test_forge_access_token(user_a):
    # change the signature of an access token and verify it is marked as invalid
    original = AccessToken(from_user=user_a)
    encoding = jwt.encode(original.jwt_data, "new_key", algorithm="HS256")
    decoded = AccessToken(from_encoding=encoding)
    assert not decoded.valid()


def test_user_token_missing_user_id():
    # create a valid token but with missing user id and
    # check that it is marked as invalid
    token = AccessToken(
        from_encoding=jwt.encode(
            {
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
                "iat": datetime.now(tz=timezone.utc),
                # missing user ID
            },
            api_settings.SIGNING_KEY,
            algorithm=api_settings.ALGORITHM,
        )
    )

    assert not token.valid()


@pytest.mark.django_db
def test_user_token_wrong_user_id():
    # create a valid token but with a non-existing user id and
    # check that it is marked as invalid
    token = UserToken(
        from_encoding=jwt.encode(
            {
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
                "iat": datetime.now(tz=timezone.utc),
                AccessToken.USER_ID_KEY: 1234,  # non-existing user
            },
            api_settings.SIGNING_KEY,
            algorithm=api_settings.ALGORITHM,
        )
    )

    assert not token.valid()


@pytest.mark.django_db
def test_refresh_token(user_a):
    # create a refresh token and verify it is marked as valid and not expired
    token = RefreshToken(from_user=user_a)
    assert token.valid()
    assert not token.expired()
    assert token.user == user_a


@pytest.mark.django_db
def test_refresh_token_save(user_a):
    # create a refresh token, save it, and verify the db object is created
    token = RefreshToken(from_user=user_a)
    db_obj = token.save()
    assert token.valid()
    assert db_obj == ActiveToken.objects.first()
    assert db_obj.owner == user_a
    assert db_obj.exp == token.iat + api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()


@pytest.mark.django_db
def test_refresh_token_blacklist(user_a):
    # create a refresh token, blacklist it, and verify it is marked as blacklisted and invalid
    token = RefreshToken(from_user=user_a)
    assert token.valid()
    token.blacklist()
    assert token.blacklisted()
    assert not token.valid()


@pytest.mark.django_db
def test_refresh_token_blacklist_inactive(user_a):
    # create a refresh token, save it, blacklist it,
    # and verify it is not among active tokens anymore
    token = RefreshToken(from_user=user_a)
    token.save()
    token.blacklist()
    assert token.blacklisted()
    assert not token.valid()
    assert ActiveToken.objects.filter(token_string=token.token_string).count() == 0


@pytest.mark.django_db
def test_refresh_token_decode_blacklist(user_a):
    # create a refresh token, blacklist it, encode it, decode it,
    # and verify it is marked as blacklisted and invalid
    original = RefreshToken(from_user=user_a)
    original.blacklist()

    decoded = RefreshToken(from_encoding=original.encoding)
    assert decoded.blacklisted()
    assert not decoded.valid()


@pytest.mark.django_db
def test_refresh_token_missing_token_string(user_a):
    # create a valid token but with a non-existing user id and
    # check that it is marked as invalid
    token = RefreshToken(
        from_encoding=jwt.encode(
            {
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
                "iat": datetime.now(tz=timezone.utc),
                AccessToken.USER_ID_KEY: user_a.id,
            },
            api_settings.SIGNING_KEY,
            algorithm=api_settings.ALGORITHM,
        )
    )

    assert not token.valid()


@pytest.mark.django_db
def test_gen_access_token(user_a):
    ref_token = RefreshToken(from_user=user_a)
    acc_token = ref_token.gen_access_token()

    assert acc_token.valid()
    assert not acc_token.expired()
    assert acc_token.user == user_a
