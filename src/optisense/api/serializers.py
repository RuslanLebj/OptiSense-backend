from rest_framework import serializers
from .models import Camera, Outlet, Record
from pydantic import ValidationError as PydanticValidationError
from .schemas import ROIPolygonsSchema, IndicatorsStatusSchema, IndicatorsSchema


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = "__all__"


class CameraSerializer(serializers.ModelSerializer):
    outlet_detail = OutletSerializer(source="outlet", read_only=True)

    class Meta:
        model = Camera
        fields = [
            "id",
            "name",
            "preview",
            "url_address",
            "connection_login",
            "connection_password",
            "start_time",
            "end_time",
            "is_active",
            "indicators_status",
            "indicators_threshold",
            "roi_polygons",
            "outlet_detail",
        ]

    @staticmethod
    def validate_roi_polygons(value):
        """
        Validate roi_polygons field using Pydantic.
        """
        if value:
            try:
                ROIPolygonsSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(f"ROI Polygons validation error: {e}")
        return value

    @staticmethod
    def validate_indicators_status(value):
        """
        Validate indicators_status field using Pydantic.
        """
        if value:
            try:
                IndicatorsStatusSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(
                    f"Indicators status validation error: {e}"
                )
        return value

    @staticmethod
    def validate_indicators_threshold(value):
        """
        Validate indicators threshold field using Pydantic.
        """
        if value:
            try:
                IndicatorsSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(f"Indicators threshold validation error: {e}")
        return value


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"

    @staticmethod
    def validate_indicators_value(value):
        """
        Validate indicators value field using Pydantic.
        """
        if value:
            try:
                IndicatorsSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(f"Indicators value validation error: {e}")
        return value
