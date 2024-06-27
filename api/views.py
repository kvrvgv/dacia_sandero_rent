import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.password_validation import (UserAttributeSimilarityValidator, MinimumLengthValidator,
                                                     CommonPasswordValidator, NumericPasswordValidator)
from django.core.validators import EmailValidator
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Client, ParkingStation, Plan, Transport, RentPeriod, RentPeriodCarUsage


# region auth


class GetMeView(APIView):
    def get(self, request: Request):
        if request.user.is_authenticated:
            return Response({"success": True, "data": request.user.json()})
        return Response({"success": False, "message": "You are not logged in"})


class LoginView(APIView):
    def post(self, request: Request):
        if request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "You are already authenticated",
            }, status=status.HTTP_400_BAD_REQUEST)
        login_ = request.data.get('login')
        password = request.data.get('password')
        if not login_ or not password:
            return Response({
                "success": False,
                "message": "Please fill out the form completely",
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            if len(password) < 8:
                raise Client.DoesNotExist()
            user = Client.objects.filter(Q(username=login_) | Q(email=login_.lower())).get()
            if not user.check_password(password):
                raise Client.DoesNotExist()

        except Client.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid Credentials",
            }, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response({
            "success": True,
            "message": "You are logged in",
            "data": user.json()
        })


class RegisterView(APIView):
    def post(self, request: Request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        password_check = request.data.get('passwordCheck')
        if not username or not password or not password_check or not email:
            return Response({
                "success": False,
                "message": "Please fill form",
            }, status=status.HTTP_400_BAD_REQUEST)
        if password != password_check:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            EmailValidator()(email)
        except ValidationError:
            return Response({
                "success": False,
                "message": "Email address is not valid",
            }, status=status.HTTP_400_BAD_REQUEST)

        if Client.objects.filter(Q(username=username) | Q(email=email.lower())).exists():
            return Response({
                "success": "error",
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
                "success": False,
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        login(request, user)
        return Response({
            "success": True,
            "message": "Your account successfully registered",
            "data": user.json(),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def get(self, request: Request):
        if request.user.is_authenticated:
            logout(request)
        return Response({"success": True})


# endregion


class AvailableTransport(APIView):
    def get(self, request: Request):
        stations = ParkingStation.objects.all()
        return Response({
            "success": True,
            "data": [station.as_dict for station in stations]
        })


class AvailablePlans(APIView):
    def get(self, request: Request):
        plans = Plan.objects.all()
        return Response({
            "success": True,
            "data": [plan.as_dict for plan in plans]
        })


class StartRide(APIView):
    def post(self, request: Request):
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "You are not authenticated",
            }, status=status.HTTP_400_BAD_REQUEST)

        car_id = request.data.get('carId')  # model id
        plan_id = request.data.get('planId')
        parking_station_id = request.data.get('parkingStationId')

        if request.user.is_on_ride:
            car = request.user.change_car(parking_station_id, car_id)
        else:
            request.user.start_rent_period(plan_id)
            car = request.user.take_car(parking_station_id, car_id)

        return Response({
            "success": True,
            "data": request.user.json(),
            "carNumber": car.registry_number
        })


class EndRide(APIView):
    def post(self, request: Request):
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "You are not authenticated",
            }, status=status.HTTP_400_BAD_REQUEST)

        parking_station_id = request.data.get('parkingStationId')
        request.user.end_all_rents(parking_station_id)

        return Response({
            "success": True,
            "data": request.user.json()
        })
