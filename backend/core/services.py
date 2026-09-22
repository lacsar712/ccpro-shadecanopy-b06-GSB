"""禁灌日历的归日（时刻 → 东八区自然日）与黑名单查询规则。

新建轮灌的拦截判断与分区列表的「今日禁灌」标记必须读同一份查询，
统一走本模块的 ``blackout_qs``，避免两处口径不一致。
"""
from zoneinfo import ZoneInfo

from django.utils import timezone

from .models import IrrigationBlackout

# 东八区（Asia/Shanghai，无夏令时）
LOCAL_TZ = ZoneInfo("Asia/Shanghai")


def local_day(dt):
    """把任意时刻归一为东八区自然日（date）。"""
    if dt is None:
        return None
    return timezone.localtime(dt, LOCAL_TZ).date()


def today_local():
    """当前时刻对应的东八区自然日。"""
    return local_day(timezone.now())


def blackout_qs(zone_id, day):
    """禁灌黑名单唯一查询：分区 + 东八区自然日。

    轮灌新建拦截与分区「今日禁灌」标记共用本查询。
    """
    return IrrigationBlackout.objects.filter(zone_id=zone_id, blackout_date=day)
