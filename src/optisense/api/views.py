from django_filters import rest_framework as filters
from rest_framework import viewsets
from .models import Camera, Outlet, Record
from .serializers import (
    CameraSerializer,
    OutletSerializer,
    RecordSerializer,
)


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
