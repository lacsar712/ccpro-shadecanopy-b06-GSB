# Generated for ShadeCanopy blackout calendar (zone irrigation blackout dates)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import core.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="IrrigationBlackout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(help_text="禁灌日，按东八区自然日归算")),
                ("reason", models.CharField(max_length=200, validators=[core.models.validate_blackout_reason])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="created_blackouts", to=settings.AUTH_USER_MODEL)),
                ("zone", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blackouts", to="core.zone")),
            ],
            options={
                "ordering": ["-date", "zone_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="irrigationblackout",
            constraint=models.UniqueConstraint(fields=("zone", "date"), name="uniq_blackout_zone_date"),
        ),
    ]
