import os
import secrets

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from eth_utils import is_address, to_checksum_address

from payroll.models import Employee, PayrollClaim, PayrollRun, PayrollSchedule
from payroll.schedule_utils import _local_now, next_daily, next_monthly, next_weekly, next_yearly

CUSDC = os.getenv("CUSDC", "")
PAYROLL_VAULT = os.getenv("PAYROLL_VAULT", "")

ZERO_REF = "0x" + "00" * 32


def _norm_addr(addr: str) -> str:
    if not addr or not isinstance(addr, str):
        raise ValueError("Missing address")
    if not is_address(addr):
        raise ValueError(f"Invalid address: {addr}")
    return to_checksum_address(addr)


def _require_env():
    if not CUSDC:
        raise RuntimeError("Missing env var CUSDC")
    if not PAYROLL_VAULT:
        raise RuntimeError("Missing env var PAYROLL_VAULT")
    _norm_addr(CUSDC)
    _norm_addr(PAYROLL_VAULT)


def generate_payroll_id(max_tries: int = 20) -> int:
    MAX_SQLITE_INT = (1 << 63) - 1

    for _ in range(max_tries):
        pid = secrets.randbits(63)
        if pid <= 0 or pid > MAX_SQLITE_INT:
            continue

        if not PayrollRun.objects.filter(payroll_id=pid).exists():
            return pid

    raise RuntimeError("Could not generate unique payroll_id")


def _compute_next_run(schedule: PayrollSchedule, after_dt):
    st = schedule.schedule_type
    if st == "daily":
        return next_daily(after_dt, schedule.time_of_day)
    if st == "weekly":
        return next_weekly(after_dt, schedule.time_of_day, schedule.weekday)
    if st == "monthly":
        return next_monthly(after_dt, schedule.time_of_day, schedule.day_of_month)
    if st == "yearly":
        return next_yearly(after_dt, schedule.time_of_day, schedule.month_of_year, schedule.day_of_year)
    return None


@shared_task
def tick_schedules():
    _require_env()

    now = _local_now()

    due = list(
        PayrollSchedule.objects.filter(
            enabled=True,
            schedule_type__in=["daily", "weekly", "monthly", "yearly"],
            next_run_at__isnull=False,
            next_run_at__lte=now,
        ).values("id")
    )

    for row in due:
        sid = row["id"]

        with transaction.atomic():
            sched = PayrollSchedule.objects.get(id=sid)

            if not sched.enabled or not sched.next_run_at or sched.next_run_at > now:
                continue

            base_time = max(now, sched.next_run_at)
            next_run = _compute_next_run(sched, base_time)
            prev_nonce = int(sched.run_nonce or 0)

            updated = PayrollSchedule.objects.filter(
                id=sid,
                run_nonce=prev_nonce,
                next_run_at=sched.next_run_at,
            ).update(
                run_nonce=prev_nonce + 1,
                next_run_at=next_run,
            )

            if updated != 1:
                continue

            employer = sched.employer
            employees = list(Employee.objects.filter(employer=employer, active=True).order_by("wallet"))
            if not employees:
                continue

            payroll_id = generate_payroll_id()
            claim_window_days = PayrollRun._meta.get_field("claim_window_days").default
            close_at = now + timezone.timedelta(days=claim_window_days)

            run = PayrollRun.objects.create(
                employer=employer,
                schedule=sched,
                run_nonce=prev_nonce + 1,
                payroll_id=payroll_id,
                token=_norm_addr(CUSDC),
                vault=_norm_addr(PAYROLL_VAULT),
                total=len(employees),
                total_amount_units=sum(int(e.salary_units) for e in employees),
                status="draft",
                claim_window_days=claim_window_days,
                close_at=close_at,
            )
            sched.last_run_at = now
            sched.save(update_fields=["last_run_at"])

            claims = [
                PayrollClaim(
                    run=run,
                    employee_wallet=_norm_addr(emp.wallet),
                    index=idx,
                    leaf="",
                    proof=[],
                    net_ciphertext_b64="",
                    encrypted_ref=ZERO_REF,
                    status="unclaimed",
                )
                for idx, emp in enumerate(employees)
            ]
            PayrollClaim.objects.bulk_create(claims)
