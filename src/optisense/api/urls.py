from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r"cameras", views.CameraViewSet)
router.register(r"camera-parameters", views.CameraParameterViewSet)
router.register(r"outlets", views.OutletViewSet)
router.register(r"parameter-types", views.ParameterTypeViewSet)
router.register(r"records", views.RecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]