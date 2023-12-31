# Generated by Django 4.2.1 on 2023-10-10 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0002_well_refresh_alter_well_pumptype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='well',
            name='Refresh',
            field=models.FloatField(blank=True, choices=[(30, '30s'), (60, '1m'), (120, '2m'), (300, '5m'), (600, '10m'), (900, '15m'), (1800, '30m')], default=120, null=True, verbose_name='Refresh'),
        ),
    ]
