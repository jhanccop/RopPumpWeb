from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0006_camerastation_schedule_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='camerastation',
            name='TimeSleepC',
            field=models.PositiveSmallIntegerField(
                choices=[(5, '5 s'), (20, '20 s'), (30, '30 s'), (60, '60 s')],
                default=30,
                verbose_name='Capture Interval (s)',
            ),
        ),
    ]
