from rest_framework import viewsets
from .models import Camera, CameraParameter, Outlet, ParameterType, Record
from .serializers import (
    CameraSerializer,
    CameraParameterSerializer,
    OutletSerializer,
    ParameterTypeSerializer,
    RecordSerializer,
)


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class CameraParameterViewSet(viewsets.ModelViewSet):
    queryset = CameraParameter.objects.all()
    serializer_class = CameraParameterSerializer


class OutletViewSet(viewsets.ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer


class ParameterTypeViewSet(viewsets.ModelViewSet):
    queryset = ParameterType.objects.all()
    serializer_class = ParameterTypeSerializer


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
