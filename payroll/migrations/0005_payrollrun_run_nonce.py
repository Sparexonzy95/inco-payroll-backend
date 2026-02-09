from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("payroll", "0004_payrollrun_schedule_payrollrun_schedule_nonce_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="payrollrun",
            name="uniq_run_per_schedule_nonce",
        ),
        migrations.RenameField(
            model_name="payrollrun",
            old_name="schedule_nonce",
            new_name="run_nonce",
        ),
        migrations.AddConstraint(
            model_name="payrollrun",
            constraint=models.UniqueConstraint(
                fields=("schedule", "run_nonce"),
                name="uniq_run_per_schedule_nonce",
                condition=Q(schedule__isnull=False),
            ),
        ),
    ]
