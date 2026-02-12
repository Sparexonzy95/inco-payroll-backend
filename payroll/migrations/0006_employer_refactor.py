from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_employer_and_profile_updates"),
        ("payroll", "0005_payrollrun_run_nonce"),
    ]

    operations = [
        migrations.RenameField(model_name="employee", old_name="org", new_name="employer"),
        migrations.RenameField(model_name="payrollrun", old_name="org", new_name="employer"),
        migrations.RenameField(model_name="payrollschedule", old_name="org", new_name="employer"),
        migrations.AlterField(
            model_name="employee",
            name="employer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="employees", to="accounts.employer"),
        ),
        migrations.AlterField(
            model_name="payrollrun",
            name="employer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payroll_runs", to="accounts.employer"),
        ),
        migrations.AlterField(
            model_name="payrollschedule",
            name="employer",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payroll_schedules", to="accounts.employer"),
        ),
        migrations.AlterUniqueTogether(name="employee", unique_together={("employer", "wallet")}),
        migrations.RemoveIndex(model_name="employee", name="payroll_emp_org_id_81a075_idx"),
        migrations.RemoveIndex(model_name="employee", name="payroll_emp_org_id_c81d17_idx"),
        migrations.RemoveIndex(model_name="payrollrun", name="payroll_pay_org_id_6e1646_idx"),
        migrations.RemoveIndex(model_name="payrollschedule", name="payroll_pay_org_id_78ab76_idx"),
        migrations.AddIndex(model_name="employee", index=models.Index(fields=["employer", "active"], name="payroll_emp_employe_d8d53d_idx")),
        migrations.AddIndex(model_name="employee", index=models.Index(fields=["employer", "wallet"], name="payroll_emp_employe_99c0fe_idx")),
        migrations.AddIndex(model_name="payrollrun", index=models.Index(fields=["employer", "status"], name="payroll_pay_employe_820e53_idx")),
        migrations.AddIndex(model_name="payrollschedule", index=models.Index(fields=["employer", "enabled"], name="payroll_pay_employe_0df177_idx")),
    ]
