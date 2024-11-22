from django_filters import rest_framework as filters
from rest_framework import viewsets
from django.db.models.expressions import RawSQL
from .models import Camera, Outlet, Record
from .serializers import (
    CameraSerializer,
    OutletSerializer,
    RecordSerializer,
)
from django.db.models import Avg, Func, FloatField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from rest_framework.response import Response
from rest_framework.decorators import action


class OutletViewSet(viewsets.ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer


class CameraFilter(filters.FilterSet):
    outlet = filters.NumberFilter(field_name="outlet")

    class Meta:
        model = Camera
        fields = ["outlet"]


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CameraFilter


class RecordFilter(filters.FilterSet):
    camera = filters.NumberFilter(field_name="camera")
    outlet = filters.NumberFilter(field_name="camera__outlet")

    class Meta:
        model = Record
        fields = ["camera", "outlet"]


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecordFilter

    @action(detail=False, methods=["get"])
    def averages(self, request):
        """
        Custom action to calculate averages grouped by day, week, or month for a specific parameter.
        """
        queryset = self.get_queryset()
        group_by = request.query_params.get("group_by", "day").lower()
        parameter_key = request.query_params.get("parameter", None)

        if not parameter_key:
            return Response({"error": "Missing required 'parameter' query parameter."}, status=400)

        group_options = {
            "day": TruncDay,
            "week": TruncWeek,
            "month": TruncMonth,
        }

        if group_by not in group_options:
            return Response(
                {"error": "Invalid 'group_by' value. Choose from 'day', 'week', or 'month'."},
                status=400,
            )

        trunc_func = group_options[group_by]

        parameter_value = RawSQL(
            f"(parameters ->> %s)::float", (parameter_key,), output_field=FloatField()
        )

        values = (
            queryset.annotate(period=trunc_func("record_time"))
            .values("period")
            .annotate(value=Avg(parameter_value))
            .order_by("period")
        )

        return Response({"values": values})