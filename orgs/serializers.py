from rest_framework import serializers
from orgs.models import Organization

class OrganizationListSerializer(serializers.ModelSerializer):
    role = serializers.CharField()

    class Meta:
        model = Organization
        fields = ["id", "name", "role"]
