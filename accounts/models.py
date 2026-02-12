from django.contrib.auth.models import User
from django.db import models


class Employer(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    wallet_address = models.CharField(max_length=42, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.wallet_address})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    wallet_address = models.CharField(max_length=42, unique=True, null=True, blank=True)
    employer = models.ForeignKey(
        Employer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
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
