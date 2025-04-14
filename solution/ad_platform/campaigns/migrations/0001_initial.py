# Generated by Django 5.1.6 on 2025-02-14 07:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("advertisers", "0002_mlscore"),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "campaign_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("impressions_limit", models.IntegerField()),
                ("clicks_limit", models.IntegerField()),
                ("cost_per_impression", models.FloatField()),
                ("cost_per_click", models.FloatField()),
                ("ad_title", models.CharField(max_length=100)),
                ("ad_text", models.TextField()),
                ("start_date", models.IntegerField()),
                ("end_date", models.IntegerField()),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("male", "male"), ("female", "female")],
                        max_length=1000,
                        null=True,
                    ),
                ),
                ("age_from", models.IntegerField()),
                ("age_to", models.IntegerField()),
                ("location", models.CharField(max_length=1000)),
                (
                    "advertiser_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="advertisers.advertiser",
                    ),
                ),
            ],
            options={
                "verbose_name": "Рекламная кампания",
                "verbose_name_plural": "Рекламные кампании",
            },
        ),
    ]
