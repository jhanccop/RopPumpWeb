# Generated by Django 4.2.1 on 2023-10-04 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_setting_tankfactor_setting_tankheight'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='DeviceType',
            field=models.CharField(choices=[('Rod Pump Analyzer', 'Rod Pump Analyzer'), ('Tank Level Meter', 'Tank Level Meter')], default='Rod Pump Analyzer', max_length=50, verbose_name='Device Type'),
        ),
    ]
