from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r"cameras", views.CameraViewSet)
router.register(r"outlets", views.OutletViewSet)
router.register(r"records", views.RecordViewSet)

urlpatterns = [
    path("", include(router.urls)),

    # Эндпоинт для получения схемы OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]