# Generated by Django 5.1.4 on 2025-01-01 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user_log",
            old_name="identify",
            new_name="identity",
        ),
    ]
