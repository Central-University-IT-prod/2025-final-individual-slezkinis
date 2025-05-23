# Generated by Django 5.1.6 on 2025-02-21 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0009_alter_campaignimage_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[("MALE", "male"), ("FEMALE", "female"), ("ALL", "all")],
                max_length=1000,
                null=True,
            ),
        ),
    ]
