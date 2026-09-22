"""禁灌日历共享查询。

「归日」与「拦截」唯一的口径来源：
- 分区列表的 todayBlackout 标记（views.ZoneViewSet）
- 新建轮灌的禁灌拦截（views.IrrigationCycleViewSet.create）
都必须经由 blackouts_on() 构造查询，保证两处读到同一查询。
"""
from zoneinfo import ZoneInfo

from django.utils import timezone

from .models import IrrigationBlackout

# 禁灌日固定按东八区自然日归算
BLACKOUT_TZ = ZoneInfo("Asia/Shanghai")


def local_day(dt):
    """归日：把一个时刻换算为东八区自然日（date）。"""
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, BLACKOUT_TZ)
    return dt.astimezone(BLACKOUT_TZ).date()


def blackouts_on(day):
    """某一天（东八区自然日）的禁灌查询集 —— 标记与拦截共用同一查询。"""
    return IrrigationBlackout.objects.filter(date=day)


def find_blackout(zone_id, day):
    """查某分区某东八区自然日是否命中禁灌，命中返回禁灌记录否则 None。"""
    return blackouts_on(day).filter(zone_id=zone_id).first()


def today():
    """当前时刻的东八区自然日。"""
    return local_day(timezone.now())
