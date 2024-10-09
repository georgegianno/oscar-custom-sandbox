# Generated by Django 4.2.16 on 2024-10-09 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("offer", "0014_range_parents_only"),
    ]

    operations = [
        migrations.AlterField(
            model_name="range",
            name="parents_only",
            field=models.BooleanField(
                default=False, verbose_name="Standalone and parents only"
            ),
        ),
    ]
