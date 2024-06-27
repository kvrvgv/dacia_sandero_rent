

import random
from datetime import datetime
from typing import Optional

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count
from django.conf import settings


class Client(AbstractUser):
    rating = models.IntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "rating": self.rating,
            "onRide": self.is_on_ride
        }

    @property
    def is_on_ride(self) -> bool:
        return RentPeriod.objects.filter(client=self, finished_at__isnull=True).exists()

    @property
    def active_rent_period(self) -> "RentPeriod":
        return RentPeriod.objects.filter(client=self, finished_at__isnull=True).first()

    @property
    def active_car_usage_period(self) -> "RentPeriodCarUsage":
        return RentPeriodCarUsage.objects.filter(period=self.active_rent_period, finished_at__isnull=True).first()

    def end_all_rents(self, parking_station_id: int):
        self.active_rent_period.end_period(parking_station_id)

    def start_rent_period(self, plan_id: int):
        rent_period = RentPeriod(client=self, plan_id=plan_id)
        rent_period.save()
        return rent_period

    def take_car(self, parking_station_id: int, transport_id: int):
        car = Transport.get_car_by_parking_and_model(parking_station_id, transport_id)
        car.parking = None
        car.save()

        rent_period_car_usage = RentPeriodCarUsage(
            period=self.active_rent_period,
            transport=car,
            starting_station_id=parking_station_id
        )
        rent_period_car_usage.save()
        return car

    def change_car(self, parking_station_id: int, new_transport_id: int):
        self.active_car_usage_period.end_period(parking_station_id)
        car = self.take_car(parking_station_id, new_transport_id)
        return car


class TransportType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class TransportClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    minimal_rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])

    def __str__(self):
        return self.name

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "minimalRating": self.minimal_rating,
        }


class TransportModel(models.Model):
    type = models.ForeignKey("TransportType", on_delete=models.CASCADE)
    classification = models.ForeignKey("TransportClass", on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(max_length=256)
    image = models.ImageField(upload_to=settings.MEDIA_ROOT / "transport_images")
    # max_fuel here if need

    def __str__(self):
        return self.name

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "type": self.type.as_dict,
            "classification": self.classification.as_dict,
            "name": self.name,
            "description": self.description,
            "imageUrl": self.image.url,
            "count": self.count if hasattr(self, "count") else None,
        }


class Transport(models.Model):
    model = models.ForeignKey("TransportModel", on_delete=models.CASCADE)
    parking = models.ForeignKey("ParkingStation", on_delete=models.SET_NULL, null=True)
    fuel = models.IntegerField(
        verbose_name="Fuel (percent)",
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    registry_number = models.CharField(max_length=50, unique=True)

    @property
    def used_by_client(self) -> Optional[Client]:
        try:
            rent_period_car_usage = RentPeriodCarUsage.objects.filter(
                transport=self, finished_at__isnull=True, finishing_station__isnull=True
            ).get()
        except RentPeriodCarUsage.DoesNotExist:
            return None
        return rent_period_car_usage.period.client

    @property
    def need_fuel(self):
        return self.fuel < 25

    def __str__(self):
        return f"{self.model.name} ({self.registry_number})"

    @classmethod
    def get_car_by_parking_and_model(cls, parking_station_id, model_id):
        return Transport.objects.filter(model_id=model_id, parking_id=parking_station_id)[:1].get()

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "parking": self.parking.as_dict,
            "model": self.model.as_dict,
            "usedByClient": self.used_by_client.json() if self.used_by_client else False,
            "fuelPercent": self.fuel,
            "registryNumber": self.registry_number,
            "needFuel": self.need_fuel,
        }

    def save(self, *args, **kwargs):
        if self.need_fuel:
            self.fuel = 100
        super().save(*args, **kwargs)


class ParkingStation(models.Model):
    address = models.CharField(max_length=150)
    short_name = models.CharField(max_length=32)
    max_cars = models.IntegerField()

    @property
    def occupancy(self):
        return Transport.objects.filter(parking=self).count()

    @property
    def available_models(self):
        return TransportModel.objects.filter(transport__parking=self).annotate(count=Count('id')).all()

    def __str__(self):
        return f"{self.short_name or self.address} ({self.occupancy} / {self.max_cars})"

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "address": self.address,
            "shortName": self.short_name,
            "maxCars": self.max_cars,
            "occupancy": self.occupancy,
            "availableModels": [m.as_dict for m in self.available_models],
        }


class Plan(models.Model):
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=255)
    time_min = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Time (Minutes)")

    def __str__(self):
        return self.name

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "timeMin": self.time_min,
        }


class RentPeriod(models.Model):
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    plan = models.ForeignKey("Plan", on_delete=models.SET_NULL, null=True)
    fine_overtime = models.IntegerField(default=0)      # todo: pre_save SIGNAL

    @property
    def active_car_usage_period(self) -> "RentPeriodCarUsage":
        return RentPeriodCarUsage.objects.filter(period=self, finished_at__isnull=True).first()

    def end_period(self, parking_station_id: int):
        self.finished_at = self.active_car_usage_period.end_period(parking_station_id)
        self.save()


class RentPeriodCarUsage(models.Model):
    period = models.ForeignKey("RentPeriod", on_delete=models.SET_NULL, null=True)
    transport = models.ForeignKey("Transport", on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    starting_station = models.ForeignKey(
        "ParkingStation", on_delete=models.SET_NULL,
        null=True, related_name="starting_station"
    )
    finishing_station = models.ForeignKey(
        "ParkingStation", on_delete=models.SET_NULL,
        null=True, related_name='finishing_station'
    )

    def end_period(self, parking_station_id: int):
        self.finished_at = datetime.now()
        self.finishing_station_id = parking_station_id
        self.transport.fuel -= random.randint(5, 25)
        self.transport.parking_id = parking_station_id
        self.transport.save()
        self.save()
        return self.finished_at


class CompanyAccounting(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=64)

    @property
    def is_income(self):
        return self.amount > 0

    @property
    def is_expense(self):
        return not self.is_income
