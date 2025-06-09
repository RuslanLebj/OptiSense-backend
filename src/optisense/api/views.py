from django_filters import rest_framework as filters
from rest_framework import viewsets
import csv
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, FloatField
from django.utils import timezone
from django.db.models.expressions import RawSQL
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from datetime import timedelta
from django.db.models.functions import ExtractHour
from unidecode import unidecode
from zoneinfo import ZoneInfo
from django.db.models.functions import TruncMinute

from .models import Camera, Outlet, Record
from .serializers import (
    CameraSerializer,
    OutletSerializer,
    RecordSerializer,
    HistoryRecordSerializer,
)
from .filters import CameraFilter, RecordFilter
from .queries import aggregate_indicators
from .handlers.threshold import ThresholdHandler
from .telegram.adapter import TelegramAdapter

telegram_adapter = TelegramAdapter()
threshold_handler = ThresholdHandler(telegram_adapter=telegram_adapter)


class FilteredModelViewSet(viewsets.ModelViewSet):
    """
    Базовый класс для ViewSet c фильтрами.
    """

    filter_backends = [filters.DjangoFilterBackend]


class OutletViewSet(FilteredModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer


class CameraViewSet(FilteredModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filterset_class = CameraFilter


class RecordViewSet(FilteredModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filterset_class = RecordFilter

    threshold_handler = threshold_handler

    def perform_create(self, serializer):
        record = serializer.save()
        self.threshold_handler.handle(record)
        return record

    @action(detail=False, methods=["get"])
    def aggregates(self, request: Request):
        """
        Агрегирует значения (avg, max, min) для указанного показателя,
        сгруппированные по дням, неделям или месяцам.
        """
        filtered_qs = self.filter_queryset(self.get_queryset())

        group_by = request.query_params.get("group_by", "day").lower()
        indicator_key = request.query_params.get("indicator")
        aggregate_type = request.query_params.get("aggregate_type", "avg").lower()
        start_date = request.query_params.get("start_date", "")
        end_date = request.query_params.get("end_date", "")
        exclude_hour_start = request.query_params.get("exclude_hour_start", "")
        exclude_hour_end = request.query_params.get("exclude_hour_end", "")

        try:
            data = aggregate_indicators(
                queryset=filtered_qs,
                group_by=group_by,
                indicator_key=indicator_key,
                aggregate_type=aggregate_type,
                start_date=start_date,
                end_date=end_date,
                exclude_hour_start=exclude_hour_start,
                exclude_hour_end=exclude_hour_end,
            )
            return Response({"values": data})
        except ValueError as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="aggregates/csv")
    def aggregates_csv(self, request: Request):
        """
        CSV с avg/max/min по каждому часовому интервалу смены камеры.
        Параметры:
          • camera (id камеры), indicator (ключ JSON) — обязательны
          • group_by — one of 'day', 'week', 'month' (по умолчанию 'day')
        """
        cam_id = request.query_params.get("camera")
        indicator = request.query_params.get("indicator")
        group_by = request.query_params.get("group_by", "day")

        if not all([cam_id, indicator]) or group_by not in ("day", "week", "month"):
            return Response(
                {
                    "error": "Нужны camera, indicator и корректный group_by (day|week|month)."
                },
                status=HTTP_400_BAD_REQUEST,
            )

        # 1) Получаем камеру
        try:
            camera = Camera.objects.select_related("outlet").get(pk=cam_id)
        except Camera.DoesNotExist:
            return Response(
                {"error": f"Камера id={cam_id} не найдена."},
                status=HTTP_400_BAD_REQUEST,
            )

        # 2) Вычисляем период
        now = timezone.now()
        if group_by == "day":
            start = now - timedelta(days=1)
        elif group_by == "week":
            start = now - timedelta(weeks=1)
        else:  # month
            start = now - timedelta(days=30)
        end = now

        # 3) Фильтрация записей по периоду и смене камеры
        qs = self.filter_queryset(self.get_queryset()).filter(
            record_time__range=(start, end)
        )
        if camera.start_time and camera.end_time:
            qs = qs.filter(
                record_time__time__gte=camera.start_time,
                record_time__time__lt=camera.end_time,
            )

        # 4) Считаем агрегаты по часам
        expr = RawSQL(
            "(indicators_value ->> %s)::float",
            (indicator,),
            output_field=FloatField(),
        )
        agg = (
            qs.annotate(hour=ExtractHour("record_time"))
            .values("hour")
            .annotate(
                avg=Avg(expr),
                max=Max(expr),
                min=Min(expr),
            )
            .order_by("hour")
        )
        data_map = {row["hour"]: row for row in agg}

        # 5) Формируем список всех интервалов смены камеры
        h_start = camera.start_time.hour if camera.start_time else 0
        h_end = camera.end_time.hour if camera.end_time else 24
        intervals = list(range(h_start, h_end))

        ## 6) Формируем безопасное ASCII имя + добавляем метку времени по ЕКБ
        ekb_tz = ZoneInfo("Asia/Yekaterinburg")
        now_ekb = now.astimezone(ekb_tz)
        ts = now_ekb.strftime("%Y%m%d_%H%M%S")
        base_raw = f"{camera.outlet.address}-{camera.name}"
        base = unidecode(base_raw).replace(" ", "_")
        filename = f"{base}-{group_by}-{ts}.csv"

        # 7) Отдаём CSV
        resp = HttpResponse(content_type="text/csv")
        resp["Access-Control-Expose-Headers"] = "Content-Disposition"
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        writer = csv.writer(resp)
        writer.writerow(["interval", "avg", "max", "min"])
        for h in intervals:
            row = data_map.get(h, {"avg": 0, "max": 0, "min": 0})
            label = f"{h}:00 - {h + 1}:00"
            writer.writerow([label, row["avg"], row["max"], row["min"]])
        return resp

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request: Request):
        """
        По одной (первой) записи на каждую минуту за последние 60 минут.
        Если в окне нет записей, окно смещается к последней доступной записи.
        """
        now = timezone.now()
        window_start = now - timedelta(minutes=60)

        qs = self.filter_queryset(self.get_queryset())

        # фильтр по камере
        cam = request.query_params.get("camera")
        if cam:
            try:
                qs = qs.filter(camera_id=int(cam))
            except ValueError:
                return Response(
                    {"error": "Invalid camera id"}, status=HTTP_400_BAD_REQUEST
                )

        # фильтр по индикатору
        indic = request.query_params.get("indicator")
        valid = {"queue_length", "service_duration"}
        if indic:
            if indic not in valid:
                return Response(
                    {"error": f"Invalid indicator, must be one of {valid}"},
                    status=HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(**{f"indicators_value__{indic}__isnull": False})

        # 1) пытаемся взять за последние 60 минут
        subset = qs.filter(record_time__gte=window_start)

        # 2) если пусто — откатываем окно к последней записи
        if not subset.exists():
            last = qs.order_by("-record_time").first()
            if not last:
                return Response([])
            end = last.record_time
            start = end - timedelta(minutes=60)
            subset = qs.filter(record_time__gte=start, record_time__lte=end)

        # 3) берём первую запись каждой минуты
        history_qs = (
            subset
            .annotate(minute=TruncMinute("record_time"))
            .order_by("minute", "record_time")
            .distinct("minute")
        )

        serializer = HistoryRecordSerializer(history_qs, many=True)
        return Response(serializer.data)