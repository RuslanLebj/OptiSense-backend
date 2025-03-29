from django.db.models import Avg, Max, Min, FloatField, QuerySet
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.db.models.expressions import RawSQL
from typing import Final
from django.utils.dateparse import parse_datetime

GROUP_BY_OPTIONS: Final = {
    "day": TruncDay,
    "week": TruncWeek,
    "month": TruncMonth,
}

AGGREGATE_FUNCTIONS: Final = {
    "avg": Avg,
    "max": Max,
    "min": Min,
}


def aggregate_indicators(
    queryset: QuerySet,
    group_by: str,
    indicator_key: str,
    aggregate_type: str,
    start_date: str | None = None,
    end_date: str | None = None,
    exclude_hour_start: str | None = None,
    exclude_hour_end: str | None = None,
) -> QuerySet:
    """
    Агрегирует значения (среднее, максимум, минимум) указанного показателя (из JSONField `indicators_value`),
    сгруппированные по периоду: дням, неделям или месяцам.
    Поддерживает фильтрацию по дате и исключение по часам суток.

    Args:
        queryset (QuerySet): QuerySet модели Record.
        group_by (str): Период группировки ('day', 'week', 'month').
        indicator_key (str): Название показателя (ключ показателя в JSONField).
        aggregate_type (str): Тип агрегации ('avg', 'max', 'min').
        start_date (str | None): Начальная дата диапазона фильтрации (ISO-формат). Например: '2024-01-01T00:00:00'.
        end_date (str | None): Конечная дата диапазона фильтрации (ISO-формат). Например: '2024-02-01T23:59:59'.
        exclude_hour_start (str | None): Начало диапазона часов, которые будут исключены (от 0 до 23).
        exclude_hour_end (str | None): Конец диапазона часов, которые будут исключены (от 0 до 23, не включительно).


    Returns:
        QuerySet: QuerySet, содержащий словари с двумя полями:
            - 'period': дата, округлённая до выбранного периода (день, неделя, месяц),
            - 'value': агрегированное числовое значение выбранного показателя за указанный период.

    Raises:
        ValueError: Если переданы некорректные значения параметров:
            - отсутствует indicator_key,
            - group_by не входит в допустимые значения,
            - aggregate_type не входит в допустимые значения,
            - start_date > end_date.
            - значения часов вне диапазона 0–23.
    """
    if not indicator_key:
        raise ValueError("Missing required 'indicator' query parameter.")

    if group_by not in GROUP_BY_OPTIONS:
        raise ValueError(
            "Invalid 'group_by'. Use one of: " + ", ".join(GROUP_BY_OPTIONS)
        )

    if aggregate_type not in AGGREGATE_FUNCTIONS:
        raise ValueError(
            "Invalid 'aggregate_type'. Use one of: " + ", ".join(AGGREGATE_FUNCTIONS)
        )

    trunc_func = GROUP_BY_OPTIONS[group_by]
    aggregate_func = AGGREGATE_FUNCTIONS[aggregate_type]

    start_date_dt = parse_datetime(start_date) if start_date else None
    end_date_dt = parse_datetime(end_date) if end_date else None

    if start_date_dt and end_date_dt and start_date_dt > end_date_dt:
        raise ValueError("Start date must be before end date.")

    if start_date_dt and end_date_dt:
        queryset = queryset.filter(record_time__range=(start_date_dt, end_date_dt))

    exclude_hour_start = (
        int(exclude_hour_start)
        if exclude_hour_start is not None and exclude_hour_start != ""
        else None
    )
    exclude_hour_end = (
        int(exclude_hour_end)
        if exclude_hour_end is not None and exclude_hour_end != ""
        else None
    )

    if (exclude_hour_start is not None and not (0 <= exclude_hour_start <= 23)) or (
        exclude_hour_end is not None and not (0 <= exclude_hour_end <= 23)
    ):
        raise ValueError("Hour values must be between 0 and 23.")

    if exclude_hour_start is not None and exclude_hour_end is not None:
        queryset = queryset.exclude(
            record_time__hour__gte=exclude_hour_start,
            record_time__hour__lt=exclude_hour_end,
        )

    indicator_expr = RawSQL(
        "(indicators_value ->> %s)::float", (indicator_key,), output_field=FloatField()
    )

    return (
        queryset.annotate(period=trunc_func("record_time"))
        .values("period")
        .annotate(value=aggregate_func(indicator_expr))
        .order_by("period")
    )