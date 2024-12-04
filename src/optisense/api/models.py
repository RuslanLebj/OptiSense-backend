# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser


class Camera(models.Model):
    outlet = models.ForeignKey("Outlet", models.DO_NOTHING)
    name = models.CharField(max_length=120)
    preview = models.CharField(max_length=255, blank=True, null=True)
    url_address = models.CharField(max_length=80)
    connection_login = models.CharField(max_length=50)
    connection_password = models.CharField(max_length=50)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_active = models.BooleanField()
    parameter_types = models.JSONField(blank=True, null=True)
    parameter_limits = models.JSONField(blank=True, null=True)
    roi_polygons_points = models.JSONField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "camera"


class Outlet(models.Model):
    address = models.CharField(max_length=255)

    class Meta:
        # managed = False
        db_table = "outlet"


class Record(models.Model):
    camera = models.ForeignKey(Camera, models.DO_NOTHING)
    record_time = models.DateTimeField()
    record_video = models.CharField(max_length=255, blank=True, null=True)
    record_frame = models.CharField(max_length=255, blank=True, null=True)
    parameters = models.JSONField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "record"


class CustomUser(AbstractUser):
    telegram_user_id = models.CharField(max_length=50, blank=True, null=True)
    telegram_user_name = models.CharField(max_length=50, blank=True, null=True)
