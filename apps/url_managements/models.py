import uuid

from django.db import models
from django.conf import settings

from .utils import generate_redirect_identifier


class RedirectRule(models.Model):
    """
    URL redirection rule configuration model.
    """

    id = models.UUIDField(
        "id", primary_key=True, editable=False, unique=True, default=uuid.uuid4
    )
    created = models.DateTimeField(
        "Date and time when object is created", auto_now_add=True
    )
    modified = models.DateTimeField(
        "Date and time when object is updated", auto_now=True
    )
    redirect_url = models.URLField("The URL where the redirect will lead")
    is_private = models.BooleanField(
        "Restrict access to unauthenticated users?", default=True
    )
    redirect_identifier = models.CharField(
        "Short unique identifier for redirect rule",
        max_length=20,
        unique=True,
        default=generate_redirect_identifier,
        editable=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="redirect_rules",
        verbose_name="Owner of the redirect rule",
    )

    class Meta:
        verbose_name = "Redirect rule"
        verbose_name_plural = "Redirect rules"
        db_table = "redirect_rules"

    def __str__(self) -> str:
        return f"{self.redirect_identifier} -> {self.redirect_url}"
