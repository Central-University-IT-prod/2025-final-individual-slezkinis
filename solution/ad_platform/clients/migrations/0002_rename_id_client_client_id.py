# Generated by Django 5.1.6 on 2025-02-13 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="client",
            old_name="id",
            new_name="client_id",
        ),
    ]
