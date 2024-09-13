from calendar import timegm
from datetime import datetime, timedelta, timezone

import jwt
from django.contrib.auth import get_user_model

from jwtauth.models import ActiveToken, BlacklistedToken
from jwtauth.settings import api_settings
from jwtauth.utils import generate_unique_token

IAT = "iat"
EXP = "exp"

UserModel = get_user_model()


class Token:
    registered_claims = [IAT, EXP]

    def __init__(
        self,
        from_encoding: str = None,
        from_data: dict = None,
        duration: timedelta = None,
    ):
        """
        Initialize a JWT token, either decoding it from a string or encoding it from data.

        :param from_encoding: The encoded token string. If this is provided,
            the token will be decoded.
        :param from_data: The data to encode into this token. If this is provided,
            the token will be encoded.
        :param duration: The duration for which the token is valid. Converted into integer
            seconds and used to set the expiration field of the JWT.
        """
        if not from_encoding and not from_data:
            raise Exception("Please specify either the data or the encoding to create the token.")

        if from_encoding and from_data:
            raise Exception(
                "Please specify either the data to encode the token or the "
                "encoding from which to derive the data, not both."
            )

        if from_data and not timedelta:
            raise Exception("Please specify a duration for the token.")

        self.data = None
        self.encoding = None

        self.jwt_data = None  # user data + jwt fields
        self.is_valid = None

        # jwt data
        self.iat = None
        self.exp = None

        if from_encoding:
            self.is_valid = self.decode(from_encoding)

        else:
            self.duration = int(duration.total_seconds())
            self.encode(from_data)
            self.is_valid = True

    def encode(self, data) -> None:
        self.data = data

        # time in seconds since epoch
        self.iat = timegm(datetime.now(tz=timezone.utc).utctimetuple())
        self.exp = self.iat + self.duration

        self.jwt_data = {
            **self.data,
            IAT: self.iat,
            EXP: self.exp,
        }

        self.encoding = jwt.encode(self.jwt_data, api_settings.SIGNING_KEY, algorithm=api_settings.ALGORITHM)

    def decode(self, data) -> bool:
        self.encoding = data

        try:
            self.jwt_data = jwt.decode(
                self.encoding,
                api_settings.SIGNING_KEY,
                algorithms=[api_settings.ALGORITHM],
                options={
                    # if the token is expired we still want to have an instance with expired=True,
                    # thus we verify exp ourselves rather than having jwt throw an exception
                    "verify_exp": False,
                    "require": self.registered_claims,
                },
            )

            self.data = self.jwt_data.copy()

            # remove jwt registered claims from user data
            for k in Token.registered_claims:
                self.data.pop(k)

            self.iat = self.jwt_data[IAT]
            self.exp = self.jwt_data[EXP]

            return True

        except jwt.InvalidTokenError:
            return False

    def valid(self) -> bool:
        return self.is_valid

    def expired(self) -> bool:
        if not self.valid():
            raise Exception("An invalid token cannot be tested for expiration.")

        return datetime.now(tz=timezone.utc).timestamp() > self.exp

    def __str__(self) -> str:
        return self.encoding


class UserToken(Token):
    """A token that is associated with a user.

    This token is used by both access and refresh tokens.
    """

    USER_ID_KEY = "user_id"

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def encode(self, user, data=None) -> None:
        self.user = user

        super().encode({**(data or {}), self.USER_ID_KEY: user.id})

    def decode(self, data) -> bool:
        if not super().decode(data):
            return False

        if self.USER_ID_KEY not in self.jwt_data:
            return False

        try:
            self.user = UserModel.objects.get(id=self.jwt_data[self.USER_ID_KEY])

        except UserModel.DoesNotExist:
            # no user with the given ID
            return False

        except UserModel.MultipleObjectsReturned:
            # multiple users with the same ID
            return False

        return True


class AccessToken(UserToken):
    def __init__(
        self,
        from_encoding=None,
        from_user=None,
        duration=api_settings.ACCESS_TOKEN_LIFETIME,
    ):
        super().__init__(
            from_encoding=from_encoding,
            from_data=from_user,
            duration=duration,
        )


class RefreshToken(UserToken):
    TOKEN_STRING_KEY = "token_string"

    def __init__(
        self,
        from_encoding=None,
        from_user=None,
        duration=api_settings.REFRESH_TOKEN_LIFETIME,
    ):
        self.token_string = None
        super().__init__(
            from_encoding=from_encoding,
            from_data=from_user,
            duration=duration,
        )

    def encode(self, user, data=None) -> None:
        self.token_string = generate_unique_token()
        super().encode(user, {self.TOKEN_STRING_KEY: self.token_string})

    def decode(self, data) -> bool:
        if not super().decode(data):
            return False

        if self.TOKEN_STRING_KEY not in self.data:
            return False

        self.token_string = self.data[self.TOKEN_STRING_KEY]
        return True

    def save(self) -> ActiveToken:
        if not self.valid():
            raise Exception("Invalid token cannot be saved!")

        mod = ActiveToken(token_string=self.token_string, owner=self.user, exp=self.exp)

        mod.save()
        return mod

    def blacklist(self) -> None:
        if not self.valid():
            raise Exception("Invalid token cannot be blacklisted!")

        ActiveToken.objects.filter(token_string=self.token_string).delete()

        mod = BlacklistedToken(token_string=self.token_string, exp=self.exp)

        mod.save()

    def blacklisted(self) -> bool:
        if not self.is_valid:
            raise Exception("Invalid token cannot be evaluated against the blacklist!")

        return BlacklistedToken.objects.filter(token_string=self.token_string).exists()

    def gen_access_token(self) -> AccessToken:
        if not self.valid():
            raise Exception("Invalid token cannot be used to generate an authentication token!")

        return AccessToken(from_user=self.user)

    def valid(self) -> bool:
        return AccessToken.valid(self) and not self.blacklisted()
