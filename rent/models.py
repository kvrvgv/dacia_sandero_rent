

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class Client(AbstractUser):
    rating = models.IntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])
