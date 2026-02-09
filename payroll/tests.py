from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from eth_utils import to_checksum_address

from orgs.models import Organization
from payroll.models import Employee, PayrollSchedule, PayrollRun
from payroll.tasks import tick_schedules


class TickSchedulesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass")
        self.org = Organization.objects.create(name="Acme", owner=self.user)
        self.wallets = [
            to_checksum_address("0x" + "1" * 40),
            to_checksum_address("0x" + "2" * 40),
        ]
        for wallet in self.wallets:
            Employee.objects.create(org=self.org, wallet=wallet, salary_units=100)

        self.token = to_checksum_address("0x" + "a" * 40)
        self.vault = to_checksum_address("0x" + "b" * 40)

        import payroll.tasks as tasks_module

        tasks_module.CUSDC = self.token
        tasks_module.PAYROLL_VAULT = self.vault

    def test_tick_schedules_creates_single_run(self):
        now = timezone.localtime(timezone.now())
        sched = PayrollSchedule.objects.create(
            org=self.org,
            name="Daily",
            schedule_type="daily",
            time_of_day=now.time(),
            enabled=True,
            next_run_at=now - timezone.timedelta(minutes=1),
        )

        tick_schedules()

        runs = PayrollRun.objects.filter(schedule=sched)
        self.assertEqual(runs.count(), 1)
        run = runs.first()
        self.assertEqual(run.claims.count(), len(self.wallets))

    def test_tick_schedules_is_idempotent(self):
        now = timezone.localtime(timezone.now())
        sched = PayrollSchedule.objects.create(
            org=self.org,
            name="Daily",
            schedule_type="daily",
            time_of_day=now.time(),
            enabled=True,
            next_run_at=now - timezone.timedelta(minutes=1),
        )

        tick_schedules()
        tick_schedules()

        runs = PayrollRun.objects.filter(schedule=sched)
        self.assertEqual(runs.count(), 1)
