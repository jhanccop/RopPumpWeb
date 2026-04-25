import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0005_specieslabel'),
    ]

    operations = [
        migrations.AddField(
            model_name='camerastation',
            name='TurnOnTime',
            field=models.TimeField(default=datetime.time(10, 0), verbose_name='Turn On Time'),
        ),
        migrations.AddField(
            model_name='camerastation',
            name='TurnOffTime',
            field=models.TimeField(default=datetime.time(17, 0), verbose_name='Turn Off Time'),
        ),
        migrations.AddField(
            model_name='camerastation',
            name='TimeSleep',
            field=models.CharField(
                choices=[('5m', '5 minutes'), ('30m', '30 minutes'), ('1h', '1 hour')],
                default='1h', max_length=5, verbose_name='Time Sleep',
            ),
        ),
        migrations.AddField(
            model_name='camerastation',
            name='Sensitivity',
            field=models.FloatField(default=0.6, verbose_name='Sensitivity (0–1)'),
        ),
    ]
