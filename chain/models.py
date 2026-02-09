from django.db import models
from orgs.models import Organization

class ChainTx(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("failed", "Failed"),
    ]

    KIND = [
        ("create_payroll", "create_payroll"),
        ("fund_vault", "fund_vault"),
        ("claim", "claim"),
        ("deposit_wrap", "deposit_wrap"),
        ("withdraw_unwrap", "withdraw_unwrap"),
    ]

    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    chain_id = models.IntegerField()
    tx_hash = models.CharField(max_length=66, unique=True)
    kind = models.CharField(max_length=30, choices=KIND)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    # links
    run_id = models.IntegerField(null=True, blank=True)
    payroll_id = models.BigIntegerField(null=True, blank=True)
    employee_wallet = models.CharField(max_length=42, blank=True, default="")

    # receipt data
    block_number = models.BigIntegerField(null=True, blank=True)
    success = models.BooleanField(null=True, blank=True)

    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
