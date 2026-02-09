from django.db import models
from orgs.models import Organization


class Employee(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="employees")
    wallet = models.CharField(max_length=42, db_index=True)
    salary_units = models.BigIntegerField()  # USDC has 6 decimals
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("org", "wallet")
        indexes = [
            models.Index(fields=["org", "active"]),
            models.Index(fields=["org", "wallet"]),
        ]

    def __str__(self):
        return f"{self.org_id}:{self.wallet}"


class PayrollSchedule(models.Model):
    TYPE_CHOICES = [
        ("instant", "Instant"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="payroll_schedules")
    name = models.CharField(max_length=120)
    schedule_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    time_of_day = models.TimeField(null=True, blank=True)
    weekday = models.IntegerField(null=True, blank=True)       # 0..6
    day_of_month = models.IntegerField(null=True, blank=True)  # 1..31
    month_of_year = models.IntegerField(null=True, blank=True) # 1..12
    day_of_year = models.IntegerField(null=True, blank=True)   # 1..31

    enabled = models.BooleanField(default=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    # SQLite-safe dedupe fields for "claiming" a schedule tick
    last_run_at = models.DateTimeField(null=True, blank=True)
    run_nonce = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["enabled", "next_run_at"]),
            models.Index(fields=["org", "enabled"]),
        ]

    def __str__(self):
        return f"{self.org_id} {self.name} {self.schedule_type}"


class PayrollRun(models.Model):
    STATUS = [
        ("draft", "Draft"),
        ("committed", "Committed"),
        ("onchain_created", "Onchain Created"),
        ("funded", "Funded"),
        ("open", "Open for Claims"),
        ("closed", "Closed"),
    ]

    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="payroll_runs")

    # Link runs to schedules (nullable for instant runs)
    schedule = models.ForeignKey(
        PayrollSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="runs",
    )

    # Distinct from PayrollSchedule.run_nonce (this is the nonce value copied into the run)
    schedule_nonce = models.IntegerField(null=True, blank=True)

    payroll_id = models.BigIntegerField(unique=True)

    token = models.CharField(max_length=42)
    vault = models.CharField(max_length=42)

    merkle_root = models.CharField(max_length=66, blank=True, default="")
    total = models.IntegerField(default=0)
    total_amount_units = models.BigIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS, default="draft")

    create_tx_hash = models.CharField(max_length=66, blank=True, default="")
    fund_tx_hash = models.CharField(max_length=66, blank=True, default="")

    claim_window_days = models.IntegerField(default=14)
    close_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["org", "status"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["payroll_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "schedule_nonce"],
                name="uniq_run_per_schedule_nonce",
                condition=models.Q(schedule__isnull=False),
            )
        ]

    def __str__(self):
        return f"{self.org_id}:{self.payroll_id} ({self.status})"


class PayrollClaim(models.Model):
    STATUS = [("unclaimed", "Unclaimed"), ("claimed", "Claimed")]

    run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name="claims")
    employee_wallet = models.CharField(max_length=42, db_index=True)
    index = models.IntegerField()

    leaf = models.CharField(max_length=66, blank=True, default="")
    proof = models.JSONField(default=list)

    net_ciphertext_b64 = models.TextField(blank=True, default="")
    encrypted_ref = models.CharField(max_length=66, blank=True, default="0x" + "00" * 32)

    status = models.CharField(max_length=20, choices=STATUS, default="unclaimed")

    claim_tx_hash = models.CharField(max_length=66, blank=True, default="")
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("run", "employee_wallet")
        indexes = [
            models.Index(fields=["run", "index"]),
            models.Index(fields=["employee_wallet", "status"]),
        ]

    def __str__(self):
        return f"{self.run_id}:{self.employee_wallet}:{self.status}"
