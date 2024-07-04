from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Configuration du schéma Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Documentation des API pour le projet Complaints Orange RDC",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@orange-rdc.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('compliance', include('clients.urls')),  # Inclure vos URL d'application (en supposant que vous ayez "complaints" au lieu de "clients")
    path('', include('user.urls')),  # Inclure vos URL d'authentification
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
