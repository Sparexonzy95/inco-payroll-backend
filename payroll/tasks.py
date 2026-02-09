import os
import secrets
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from eth_utils import is_address, to_checksum_address

from payroll.models import PayrollSchedule, PayrollRun, Employee, PayrollClaim
from payroll.schedule_utils import _local_now, next_daily, next_weekly, next_monthly, next_yearly

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


def generate_payroll_id(max_tries: int = 10) -> int:
    """
    SQLite-safe, collision-resistant payrollId generator.
    Produces a uint256-like int (we use 96 bits).
    """
    for _ in range(max_tries):
        pid = secrets.randbits(96)
        if pid == 0:
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
    """
    Runs every minute (Celery Beat).
    Creates ONE draft PayrollRun per due schedule occurrence, even on SQLite.

    SQLite note:
    - select_for_update is ignored
    - so we use an atomic UPDATE as a lock (compare-and-swap using run_nonce)
    """
    _require_env()

    now = _local_now()

    due = list(
        PayrollSchedule.objects.filter(
            enabled=True,
            schedule_type__in=["daily", "weekly", "monthly", "yearly"],
            next_run_at__isnull=False,
            next_run_at__lte=now,
        ).values("id", "run_nonce", "next_run_at")
    )

    for row in due:
        sid = row["id"]
        prev_nonce = int(row["run_nonce"] or 0)

        # Compute the next run time based on "now"
        # We do this outside first, then confirm inside transaction.
        with transaction.atomic():
            # Re-fetch the schedule inside transaction (latest data)
            sched = PayrollSchedule.objects.get(id=sid)

            if not sched.enabled or not sched.next_run_at or sched.next_run_at > now:
                continue

            # Compute next_run_at
            next_run = _compute_next_run(sched, now)

            # Atomic lock: only one worker can bump run_nonce from prev -> prev+1
            updated = PayrollSchedule.objects.filter(
                id=sid,
                run_nonce=prev_nonce,
                next_run_at=sched.next_run_at,  # ensures we are locking this exact due occurrence
            ).update(
                run_nonce=prev_nonce + 1,
                last_run_at=now,
                next_run_at=next_run,
            )

            if updated != 1:
                # Another worker already processed this schedule occurrence
                continue

            # We are the winner for this schedule tick
            org = sched.org
            employees = list(Employee.objects.filter(org=org, active=True).order_by("wallet"))

            # If no employees, we still advanced schedule, so just skip run creation
            if not employees:
                continue

            payroll_id = generate_payroll_id()

            # Create the run linked to this schedule + the nonce we just assigned
            run = PayrollRun.objects.create(
                org=org,
                schedule=sched,
                schedule_nonce=prev_nonce + 1,
                payroll_id=payroll_id,
                token=_norm_addr(CUSDC),
                vault=_norm_addr(PAYROLL_VAULT),
                total=len(employees),
                total_amount_units=sum(int(e.salary_units) for e in employees),
                status="draft",
                close_at=None,
            )

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
