from django_filters import rest_framework as filters

from .models import Camera, Record


class CameraFilter(filters.FilterSet):
    outlet = filters.NumberFilter(field_name="outlet")

    class Meta:
        model = Camera
        fields = ["outlet"]


class RecordFilter(filters.FilterSet):
    camera = filters.NumberFilter(field_name="camera")
    outlet = filters.NumberFilter(field_name="camera__outlet")

    class Meta:
        model = Record
        fields = ["camera", "outlet"]