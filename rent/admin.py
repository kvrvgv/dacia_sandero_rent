

from django.contrib import admin

from . import models


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Transport)
class TransportAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ParkingStation)
class ParkingStationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Plan)
class PlansAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RentPeriod)
class RentPeriodAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RentPeriodCarUsage)
class RentPeriodCarUsageAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CompanyAccounting)
class CompanyAccountingAdmin(admin.ModelAdmin):
    pass
