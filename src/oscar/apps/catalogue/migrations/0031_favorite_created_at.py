# Generated by Django 4.2.16 on 2024-10-09 01:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        (
            "catalogue",
            "0030_remove_favorite_created_at_alter_favorite_product_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="favorite",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]