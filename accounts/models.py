from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    wallet = models.CharField(max_length=42, unique=True, null=True, blank=True)
    active_org = models.ForeignKey(
        "orgs.Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="active_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class WalletNonce(models.Model):
    wallet = models.CharField(max_length=42, db_index=True)
    nonce = models.CharField(max_length=128)
    message = models.TextField()
    issued_at = models.DateTimeField(auto_now_add=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["wallet", "nonce", "consumed_at"])]
