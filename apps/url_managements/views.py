from uuid import UUID

from django.contrib.auth.models import AbstractUser

from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RedirectRule
from .serializers import RedirectRuleSerializer
from .services import RedirectRuleService


class RedirectRuleListAPIView(APIView):
    """
    APIView for listing all redirect rules
    for the current user (GET) and creating
    a new redirect rule (POST).
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request: Request) -> Response:
        """
        List all redirect rules owned by the current user.
        """
        rules = RedirectRuleService.get_all_rules_for_user(request.user)
        serializer = RedirectRuleSerializer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def post(request: Request) -> Response:
        serializer = RedirectRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectRuleDetailAPIView(APIView):
    """
    APIView for updating (via PATCH) and deleting a redirect rule.

    The rule's unique identifier (UUID) is expected as part of the URL.
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get_object(pk: UUID, user: AbstractUser) -> RedirectRule:
        return get_object_or_404(RedirectRule, pk=pk, owner=user)

    def patch(self, request: Request, pk: UUID) -> Response:
        rule = self.get_object(pk, request.user)
        serializer = RedirectRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: UUID) -> Response:
        rule = self.get_object(pk, request.user)
        RedirectRuleService(rule).delete_rule()
        return Response(status=status.HTTP_204_NO_CONTENT)


redirect_url_list = RedirectRuleListAPIView.as_view()
redirect_url_detail = RedirectRuleDetailAPIView.as_view()
