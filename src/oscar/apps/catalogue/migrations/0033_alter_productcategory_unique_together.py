# Generated by Django 4.2.16 on 2024-10-11 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0032_productcategory_display_order"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productcategory",
            unique_together=set(),
        ),
    ]
