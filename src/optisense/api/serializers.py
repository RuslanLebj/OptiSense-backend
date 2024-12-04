from rest_framework import serializers
from .models import Camera, Outlet, Record
from pydantic import ValidationError as PydanticValidationError
from .schemas import ROIPolygonsPointsSchema, ParameterTypesSchema, ParametersSchema


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
            "parameter_types",
            "parameter_limits",
            "roi_polygons_points",
            "outlet_detail",
        ]

    @staticmethod
    def validate_roi_polygons_points(value):
        """
        Validate roi_polygons_points field using Pydantic.
        """
        if value:
            try:
                ROIPolygonsPointsSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(
                    f"ROI Polygons Points validation error: {e}"
                )
        return value

    @staticmethod
    def validate_parameter_types(value):
        """
        Validate parameter_types field using Pydantic.
        """
        if value:
            try:
                ParameterTypesSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(
                    f"Parameter Types validation error: {e}"
                )
        return value

    @staticmethod
    def validate_parameter_limits(value):
        """
        Validate parameter limits field using Pydantic.
        """
        if value:
            try:
                ParametersSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(f"Parameters validation error: {e}")
        return value


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"

    @staticmethod
    def validate_parameters(value):
        """
        Validate parameters field using Pydantic.
        """
        if value:
            try:
                ParametersSchema.model_validate(value)
            except PydanticValidationError as e:
                raise serializers.ValidationError(f"Parameters validation error: {e}")
        return value
