# Generated by Django 5.2.4 on 2025-07-15 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0005_alter_shop_address_alter_shop_business_license_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='tip_top',
            field=models.BooleanField(default=False),
        ),
    ]
