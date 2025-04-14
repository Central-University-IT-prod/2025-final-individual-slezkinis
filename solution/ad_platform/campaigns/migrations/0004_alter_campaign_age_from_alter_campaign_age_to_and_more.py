# Generated by Django 5.1.6 on 2025-02-14 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0003_alter_campaign_advertiser_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="age_from",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="age_to",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="campaign",
            name="location",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
