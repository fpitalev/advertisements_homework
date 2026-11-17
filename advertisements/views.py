from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement
from advertisements.permissions import IsAdvertisementAuthor
from advertisements.serializers import AdvertisementSerializer


class AdvertisementAnonRateThrottle(AnonRateThrottle):
    rate = "10/min"


class AdvertisementUserRateThrottle(UserRateThrottle):
    rate = "20/min"


class AdvertisementViewSet(ModelViewSet):
    queryset = Advertisement.objects.select_related("creator").all()
    serializer_class = AdvertisementSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AdvertisementFilter
    throttle_classes = (AdvertisementAnonRateThrottle, AdvertisementUserRateThrottle)

    def get_permissions(self):
        if self.action == "create":
            permission_classes = (IsAuthenticated,)
        elif self.action in ("update", "partial_update", "destroy"):
            permission_classes = (IsAuthenticated, IsAdvertisementAuthor)
        else:
            permission_classes = (AllowAny,)
        return [permission() for permission in permission_classes]
