

from django.contrib.auth import login
from django.contrib.auth.password_validation import (UserAttributeSimilarityValidator, MinimumLengthValidator,
                                                     CommonPasswordValidator, NumericPasswordValidator)
from django.core.validators import EmailValidator
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Client


class LoginView(APIView):
    def post(self, request: Request):
        if request.user.is_authenticated:
            return Response({
                "status": "error",
                "message": "You are already authenticated",
            }, status=status.HTTP_400_BAD_REQUEST)
        username_or_email = request.data.get('username')
        password = request.data.get('password')
        if not username_or_email or not password:
            return Response({
                'status': 'error',
                'message': 'Please fill out the form completely',
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if len(password) < 8:
                raise Client.DoesNotExist()
            user = Client.objects.filter(
                Q(username=username_or_email) | Q(email=username_or_email.lower())
            ).get()
            if not user.check_password(password):
                raise Client.DoesNotExist()

        except Client.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Invalid Credentials",
            }, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response({
            "status": "success",
            "message": "You are logged in",
        })


class RegisterView(APIView):
    def post(self, request: Request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        password_check = request.data.get('passwordCheck')
        if not username or not password or not password_check or not email:
            return Response({
                "status": "error",
                "message": "Please fill form",
            }, status=status.HTTP_400_BAD_REQUEST)
        if password != password_check:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            EmailValidator()(email)
        except ValidationError:
            return Response({
                "status": "error",
                "message": "Email address is not valid",
            }, status=status.HTTP_400_BAD_REQUEST)

        if Client.objects.filter(Q(username=username) | Q(email=email.lower())).exists():
            return Response({
                "status": "error",
                "message": "User with this email address or username already exists",
            }, status=status.HTTP_400_BAD_REQUEST)

        user = Client(email=email.lower(), username=username)

        try:
            for validator in [
                UserAttributeSimilarityValidator(), MinimumLengthValidator(8),
                CommonPasswordValidator(), NumericPasswordValidator()
            ]:
                validator.validate(password, user)
        except ValidationError as e:
            return Response({
                "status": "error",
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        login(request, user)
        return Response({
            "status": "success",
            "message": "Your account successfully registered",
        }, status=status.HTTP_201_CREATED)
