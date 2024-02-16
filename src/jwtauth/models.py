from django.db import models
from django.contrib.auth import get_user_model


class BlacklistedToken(models.Model):
    token_string = models.CharField(max_length=30, unique=True)
    exp = models.IntegerField()


class ActiveToken(models.Model):
    token_string = models.CharField(max_length=30, unique=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    exp = models.IntegerField()
