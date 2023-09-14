# Generated by Django 4.2.1 on 2023-09-07 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_remove_setting_refreshtime_setting_refresh'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='Available',
            field=models.BooleanField(choices=[(True, 'available'), (False, 'not available')], default=True, verbose_name='Available'),
        ),
        migrations.AlterField(
            model_name='setting',
            name='Refresh',
            field=models.FloatField(blank=True, choices=[(30, '30s'), (60, '1m'), (120, '2m'), (300, '5m'), (600, '10m'), (900, '15m'), (1800, '30m')], default='300', null=True, verbose_name='Refresh'),
        ),
    ]