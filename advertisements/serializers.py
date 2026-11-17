from django.contrib.auth import get_user_model
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name")


class AdvertisementSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Advertisement
        fields = ("id", "title", "description", "creator", "status", "created_at")
        read_only_fields = ("id", "creator", "created_at")

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return data

        new_status = data.get(
            "status",
            self.instance.status if self.instance else AdvertisementStatusChoices.OPEN,
        )

        if new_status == AdvertisementStatusChoices.OPEN:
            open_ads = Advertisement.objects.filter(
                creator=request.user,
                status=AdvertisementStatusChoices.OPEN,
            )
            if self.instance is not None:
                open_ads = open_ads.exclude(pk=self.instance.pk)
            if open_ads.count() >= 10:
                raise serializers.ValidationError({
                    "status": "Нельзя иметь больше 10 открытых объявлений."
                })

        return data
