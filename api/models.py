

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class Client(AbstractUser):
    rating = models.IntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
        }


class Transport(models.Model):
    type = models.IntegerField(
        choices=models.IntegerChoices(
            "TransportType", "VEHICLE BICYCLE GYRO_SCOOTER MOTORCYCLE"
        )
    )
    classification = models.IntegerField(
        choices=models.IntegerChoices(
            "TransportClassification", "ECONOM COMFORT BUSINESS ELITE"
        )
    )
    parking = models.ForeignKey("ParkingStation", on_delete=models.SET_NULL, null=True)
    fuel = models.IntegerField(
        verbose_name="Fuel (percent)",
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    minimal_rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])

    @property
    def need_fuel(self):
        return self.fuel < 25


class ParkingStation(models.Model):
    address = models.CharField(max_length=150)
    short_name = models.CharField(max_length=32)
    max_cars = models.IntegerField()

    @property
    def occupancy(self):
        return Transport.objects.filter(parking=self).count()

    def __str__(self):
        return f"{self.short_name or self.address} ({self.occupancy} / {self.max_cars})"


class Plan(models.Model):
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=255)
    time = models.TimeField()


class RentPeriod(models.Model):
    client = models.ForeignKey("Client", on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    plan = models.ForeignKey("Plan", on_delete=models.SET_NULL, null=True)
    fine_overtime = models.IntegerField(default=0)      # todo: pre_save SIGNAL


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


class CompanyAccounting(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=64)

    @property
    def is_income(self):
        return self.amount > 0

    @property
    def is_expense(self):
        return not self.is_income
