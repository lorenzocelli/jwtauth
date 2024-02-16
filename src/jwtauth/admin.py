from django.contrib import admin
from jwtauth.models import BlacklistedToken, ActiveToken

admin.site.register(BlacklistedToken)
admin.site.register(ActiveToken)
