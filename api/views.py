

from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse


def login(request: ASGIRequest):
    return HttpResponse("Login")


def register(request: ASGIRequest):
    return HttpResponse("Register")
