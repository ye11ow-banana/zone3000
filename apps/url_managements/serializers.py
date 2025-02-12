from rest_framework import serializers

from .models import RedirectRule


class RedirectRuleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = RedirectRule
        fields = (
            "id",
            "created",
            "modified",
            "redirect_url",
            "is_private",
            "redirect_identifier",
            "owner",
        )
        read_only_fields = ("id", "created", "modified", "redirect_identifier", "owner")
