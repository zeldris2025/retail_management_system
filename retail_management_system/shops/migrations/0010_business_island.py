# Generated by Django 5.2.4 on 2025-07-24 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0009_alter_business_business_license'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='island',
            field=models.CharField(blank=True, choices=[('Upolu', 'Upolu'), ('Savaii', 'Savaii')], default='Upolu', max_length=50, null=True),
        ),
    ]
