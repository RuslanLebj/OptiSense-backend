from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Camera, Outlet, Record
from .serializers import (
    CameraSerializer,
    OutletSerializer,
    RecordSerializer,
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