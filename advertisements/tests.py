from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from advertisements.models import Advertisement, AdvertisementStatusChoices


User = get_user_model()


class AdvertisementAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author", password="pass12345")
        self.other_user = User.objects.create_user(username="other", password="pass12345")
        self.token = Token.objects.create(user=self.user)
        self.list_url = reverse("advertisement-list")

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_is_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_requires_authentication(self):
        response = self.client.post(self.list_url, {"title": "Title", "description": "Text"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_advertisement(self):
        self.authenticate()
        response = self.client.post(
            self.list_url,
            {"title": "Title", "description": "Text"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["creator"]["id"], self.user.id)

    def test_user_cannot_create_more_than_ten_open_advertisements(self):
        Advertisement.objects.bulk_create([
            Advertisement(title=f"Ad {number}", creator=self.user)
            for number in range(10)
        ])
        self.authenticate()
        response = self.client.post(
            self.list_url,
            {"title": "Eleventh", "description": "Text"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_author_can_update_own_advertisement(self):
        advertisement = Advertisement.objects.create(title="Before", creator=self.user)
        self.authenticate()
        response = self.client.patch(
            reverse("advertisement-detail", args=[advertisement.id]),
            {"title": "After"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_update_advertisement(self):
        advertisement = Advertisement.objects.create(title="Before", creator=self.user)
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")
        response = self.client.patch(
            reverse("advertisement-detail", args=[advertisement.id]),
            {"title": "After"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_delete_advertisement(self):
        advertisement = Advertisement.objects.create(title="Title", creator=self.user)
        other_token = Token.objects.create(user=self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")
        response = self.client.delete(
            reverse("advertisement-detail", args=[advertisement.id])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_advertisement(self):
        advertisement = Advertisement.objects.create(title="Title", creator=self.user)
        self.authenticate()
        response = self.client.delete(
            reverse("advertisement-detail", args=[advertisement.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_by_status(self):
        Advertisement.objects.create(title="Open", creator=self.user)
        Advertisement.objects.create(
            title="Closed",
            creator=self.user,
            status=AdvertisementStatusChoices.CLOSED,
        )
        response = self.client.get(self.list_url, {"status": "CLOSED"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "CLOSED")
