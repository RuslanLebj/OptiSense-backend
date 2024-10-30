from rest_framework import serializers
from .models import Camera, CameraParameter, Outlet, ParameterType, Record


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"


class CameraParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraParameter
        fields = "__all__"


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = "__all__"


class ParameterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterType
        fields = "__all__"


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"
