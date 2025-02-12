from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from url_managements.models import RedirectRule

User: type[AbstractUser] = get_user_model()  # type: ignore


class AccessRedirectAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="username", password="password")
        self.public_rule = RedirectRule.objects.create(
            redirect_url="https://public.example.com",
            is_private=False,
            redirect_identifier="public123",
            owner=self.user,
        )
        self.private_rule = RedirectRule.objects.create(
            redirect_url="https://private.example.com",
            is_private=True,
            redirect_identifier="private123",
            owner=self.user,
        )

    def test_invalid_access_parameter_returns_404(self):
        """
        When 'access' is not 'public' or 'private', the view should raise NotFound.
        """
        url = reverse(
            "redirects:access_redirect",
            kwargs={"access": "invalid", "redirect_identifier": "public123"},
        )
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_private_redirect_without_authentication_returns_401(self):
        """
        For 'private' access, if the user is not authenticated, NotAuthenticated should be returned.
        """
        url = reverse(
            "redirects:access_redirect",
            kwargs={
                "access": "private",
                "redirect_identifier": self.private_rule.redirect_identifier,
            },
        )
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_redirect_success(self):
        """
        A valid public redirect should return a 302 redirect response.
        """
        url = reverse(
            "redirects:access_redirect",
            kwargs={
                "access": "public",
                "redirect_identifier": self.public_rule.redirect_identifier,
            },
        )
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], self.public_rule.redirect_url)

    def test_private_redirect_success_authenticated(self):
        """
        A valid private redirect with an authenticated user should return a 302 redirect response.
        """
        client = APIClient()
        client.force_authenticate(self.user)
        url = reverse(
            "redirects:access_redirect",
            kwargs={
                "access": "private",
                "redirect_identifier": self.private_rule.redirect_identifier,
            },
        )
        response = client.get(url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], self.private_rule.redirect_url)

    def test_rule_not_found_returns_404(self):
        """
        If no RedirectRule exists for the given identifier, the view should return a 404.
        """
        url = reverse(
            "redirects:access_redirect",
            kwargs={"access": "public", "redirect_identifier": "nonexistent"},
        )
        response = self.client.get(url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
