from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orgs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("wallet", models.CharField(blank=True, max_length=42, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "active_org",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="active_users", to="orgs.organization"),
                ),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WalletNonce",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("wallet", models.CharField(db_index=True, max_length=42)),
                ("nonce", models.CharField(max_length=128)),
                ("message", models.TextField()),
                ("issued_at", models.DateTimeField(auto_now_add=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "indexes": [models.Index(fields=["wallet", "nonce", "consumed_at"], name="accounts_wal_wallet_6f17eb_idx")],
            },
        ),
    ]
