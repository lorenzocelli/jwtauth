from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jwtauth import login, logout


@api_view(["POST"])
def login_view(request):
    body = JSONParser().parse(request)

    user = authenticate(username=body["username"], password=body["password"])

    if user is None:
        # credentials are not valid
        raise AuthenticationFailed("Invalid username or password.", 403)

    login(request, user)
    return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logged_view(request):
    return Response(status=204)


class LoggedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(status=204)


@api_view(["GET"])
def username_view(request):

    username = ""

    if request.user.is_authenticated:
        username = request.user.username

    return Response({"username": username})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=204)
