from typing import Literal

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from url_managements.models import RedirectRule


class RedirectRuleService:
    def __init__(self, rule: RedirectRule) -> None:
        self._rule = rule

    def delete_rule(self) -> None:
        self._rule.delete()

    @staticmethod
    def get_all_rules_for_user(user: AbstractUser) -> QuerySet[RedirectRule]:
        return RedirectRule.objects.filter(owner=user)

    @staticmethod
    def get_redirect_url_by_identifier(
        redirect_identifier: str,
        access: Literal["public", "private"],
    ) -> str:
        is_private = access == "private"
        try:
            rule = RedirectRule.objects.get(
                redirect_identifier=redirect_identifier, is_private=is_private
            )
        except RedirectRule.DoesNotExist:
            raise RedirectRule.DoesNotExist
        return rule.redirect_url
