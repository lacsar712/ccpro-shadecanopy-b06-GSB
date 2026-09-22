from datetime import timedelta

from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    ClimateLog,
    Greenhouse,
    IrrigationBlackout,
    IrrigationCycle,
    Zone,
)
from .serializers import (
    ClimateLogSerializer,
    GreenhouseSerializer,
    IrrigationBlackoutSerializer,
    IrrigationCycleSerializer,
    ZoneSerializer,
)
from .services import blackout_qs, local_day, today_local


class GreenhouseViewSet(viewsets.ModelViewSet):
    queryset = Greenhouse.objects.annotate(zone_count=Count("zones")).all()
    serializer_class = GreenhouseSerializer


class ZoneViewSet(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer

    def get_queryset(self):
        # 「今日禁灌」标记：与轮灌新建拦截共用 services.blackout_qs 同一查询
        qs = (
            Zone.objects.select_related("greenhouse")
            .annotate(
                blackout_today=Exists(blackout_qs(OuterRef("pk"), today_local()))
            )
            .all()
        )
        greenhouse_id = self.request.query_params.get("greenhouseId")
        status_param = self.request.query_params.get("status")
        if greenhouse_id:
            qs = qs.filter(greenhouse_id=greenhouse_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class ClimateLogViewSet(viewsets.ModelViewSet):
    serializer_class = ClimateLogSerializer

    def get_queryset(self):
        qs = ClimateLog.objects.select_related("zone", "zone__greenhouse").all()
        zone_id = self.request.query_params.get("zoneId")
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        return qs


class IrrigationCycleViewSet(viewsets.ModelViewSet):
    serializer_class = IrrigationCycleSerializer

    def get_queryset(self):
        qs = IrrigationCycle.objects.select_related("zone", "zone__greenhouse").all()
        zone_id = self.request.query_params.get("zoneId")
        status_param = self.request.query_params.get("status")
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 按开始时刻的东八区自然日查禁灌黑名单；命中则 409 并回传禁灌编号
        zone = serializer.validated_data["zone"]
        day = local_day(serializer.validated_data["start_at"])
        blackout = blackout_qs(zone.pk, day).first()
        if blackout is not None:
            return Response(
                {
                    "detail": f"{day.isoformat()} 为该分区禁灌日，禁止新建轮灌",
                    "blackoutId": blackout.pk,
                    "blackoutDate": day.isoformat(),
                    "reason": blackout.reason,
                },
                status=status.HTTP_409_CONFLICT,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class IrrigationBlackoutViewSet(viewsets.ModelViewSet):
    serializer_class = IrrigationBlackoutSerializer

    def get_queryset(self):
        qs = IrrigationBlackout.objects.select_related(
            "zone", "zone__greenhouse", "created_by"
        ).all()
        zone_id = self.request.query_params.get("zoneId")
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    now = timezone.now()
    since_24h = now - timedelta(hours=24)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    data = {
        "greenhouseCount": Greenhouse.objects.count(),
        "growingZoneCount": Zone.objects.filter(status=Zone.STATUS_GROWING).count(),
        "climateLogLast24h": ClimateLog.objects.filter(
            recorded_at__gte=since_24h
        ).count(),
        "irrigationScheduledToday": IrrigationCycle.objects.filter(
            status=IrrigationCycle.STATUS_SCHEDULED,
            start_at__gte=today_start,
            start_at__lt=today_end,
        ).count(),
    }
    return Response(data)
