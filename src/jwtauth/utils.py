from random import SystemRandom

from jwtauth.models import ActiveToken

UNICODE_ASCII_CHARACTER_SET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    """
    From OAuthLib:
    https://github.com/oauthlib/oauthlib/tree/d4b6699f8ccb608152b764919e0bd3d38a7b171f

    Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """

    rand = SystemRandom()
    return "".join(rand.choice(chars) for x in range(length))


def generate_unique_token():
    while True:
        token = generate_token()

        # loop until the token does not match an existing one;
        # the probability should be close to zero:
        # https://stats.stackexchange.com/questions/25211/simple-combination-probability-question-based-on-string-length-and-possible-char
        if not ActiveToken.objects.filter(token_string=token).exists():
            break

    return token
