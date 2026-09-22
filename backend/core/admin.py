from django.contrib import admin

from .models import ClimateLog, Greenhouse, IrrigationBlackout, IrrigationCycle, Zone


@admin.register(Greenhouse)
class GreenhouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "location", "area_m2")
    search_fields = ("name", "location")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("id", "greenhouse", "zone_code", "crop_name", "status")
    list_filter = ("status", "greenhouse")
    search_fields = ("zone_code", "crop_name")


@admin.register(ClimateLog)
class ClimateLogAdmin(admin.ModelAdmin):
    list_display = ("id", "zone", "recorded_at", "temp_c", "humidity_pct", "par_umol", "co2_ppm")
    list_filter = ("zone",)


@admin.register(IrrigationCycle)
class IrrigationCycleAdmin(admin.ModelAdmin):
    list_display = ("id", "zone", "start_at", "duration_min", "water_liters", "status")
    list_filter = ("status", "zone")


@admin.register(IrrigationBlackout)
class IrrigationBlackoutAdmin(admin.ModelAdmin):
    list_display = ("id", "zone", "blackout_date", "reason", "created_by", "created_at")
    list_filter = ("zone", "blackout_date")
    search_fields = ("reason",)
