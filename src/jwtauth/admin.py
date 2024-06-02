from django.contrib import admin

from jwtauth.models import ActiveToken, BlacklistedToken

admin.site.register(BlacklistedToken)
admin.site.register(ActiveToken)
