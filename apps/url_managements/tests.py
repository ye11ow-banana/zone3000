import uuid

from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from url_managements.models import RedirectRule

User: type[AbstractUser] = get_user_model()  # type: ignore


class RedirectRuleListAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="username", password="password")

    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("url_managements:redirect_rule_list")

    def test_get_empty_list(self) -> None:
        """
        Test that API returns an empty list when no redirect rules exist.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_create_redirect_rule(self) -> None:
        """
        Test creating a new redirect rule via POST.
        """
        data = {
            "redirect_url": "https://example.com",
            "is_private": False,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rule_id = response.data["id"]
        rule = RedirectRule.objects.get(pk=rule_id)
        self.assertEqual(rule.redirect_url, data["redirect_url"])
        self.assertEqual(rule.is_private, data["is_private"])
        self.assertEqual(rule.owner, self.user)

    def test_list_redirect_rules(self) -> None:
        """
        Test that the GET request returns all redirect rules owned by the current user.
        """
        RedirectRule.objects.create(
            redirect_url="https://example.com",
            is_private=True,
            owner=self.user,
        )
        RedirectRule.objects.create(
            redirect_url="https://anotherexample.com",
            is_private=False,
            owner=self.user,
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated(self) -> None:
        """
        Test that unauthenticated users receive a 401 response.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RedirectRuleDetailAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="username", password="password")

    def setUp(self) -> None:
        self.client: APIClient = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_patch_redirect_rule(self) -> None:
        """
        Test updating an existing redirect rule via PATCH.
        """
        rule = RedirectRule.objects.create(
            redirect_url="https://example.com", is_private=False, owner=self.user
        )
        detail_url = reverse(
            "url_managements:redirect_rule_detail", kwargs={"pk": rule.id}
        )
        patch_data = {"is_private": True}
        response = self.client.patch(detail_url, patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rule.refresh_from_db()
        self.assertTrue(rule.is_private)

    def test_delete_redirect_rule(self) -> None:
        """
        Test deleting an existing redirect rule.
        """
        rule = RedirectRule.objects.create(
            redirect_url="https://example.com", is_private=False, owner=self.user
        )
        detail_url = reverse(
            "url_managements:redirect_rule_detail", kwargs={"pk": rule.id}
        )
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RedirectRule.objects.filter(pk=rule.id).exists())

    def test_edit_or_delete_foreign_redirect_rule(self) -> None:
        """
        Test that users cannot edit or delete redirect rules owned by other users.
        """
        other_user = User.objects.create_user(
            username="other_user", password="password"
        )
        rule = RedirectRule.objects.create(
            redirect_url="https://example.com", is_private=False, owner=other_user
        )
        detail_url = reverse(
            "url_managements:redirect_rule_detail", kwargs={"pk": rule.id}
        )
        response = self.client.patch(detail_url, {"is_private": True})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated(self) -> None:
        """
        Test that unauthenticated users receive a 401 response.
        """
        self.client.force_authenticate(user=None)
        detail_url = reverse(
            "url_managements:redirect_rule_detail", kwargs={"pk": uuid.uuid4()}
        )
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_found(self) -> None:
        """
        Test that a 404 response is returned when the redirect rule does not exist.
        """
        detail_url = reverse(
            "url_managements:redirect_rule_detail", kwargs={"pk": uuid.uuid4()}
        )
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
