from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from advertisements.views import AdvertisementViewSet


router = DefaultRouter()
router.register("advertisements", AdvertisementViewSet, basename="advertisement")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
]
