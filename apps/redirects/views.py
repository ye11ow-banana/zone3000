from typing import Literal

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from rest_framework.exceptions import NotFound, NotAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from url_managements.services import RedirectRuleService


class AccessRedirectAPIView(APIView):
    """
    Redirect to the URL by the identifier.

    access: public or private.
    redirect_identifier: identifier of the redirect rule.
    """

    @staticmethod
    def get(
        request: Request, access: str, redirect_identifier: str
    ) -> HttpResponseRedirect:
        if access not in ("public", "private"):
            raise NotFound
        if access == "private" and not bool(
            request.user and request.user.is_authenticated
        ):
            raise NotAuthenticated
        try:
            access: Literal["public", "private"]
            redirect_url = RedirectRuleService.get_redirect_url_by_identifier(
                redirect_identifier, access
            )
        except ObjectDoesNotExist:
            raise NotFound
        return redirect(redirect_url)


access_redirect = AccessRedirectAPIView.as_view()
