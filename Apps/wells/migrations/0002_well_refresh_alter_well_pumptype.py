# Generated by Django 4.2.1 on 2023-10-10 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='well',
            name='Refresh',
            field=models.FloatField(blank=True, null=True, verbose_name='Refresh'),
        ),
        migrations.AlterField(
            model_name='well',
            name='PumpType',
            field=models.CharField(choices=[('Sucker Rod Pump', 'Sucker Rod Pump'), ('Plunger Lift', 'Plunger Lift')], default='Sucker Rod Pump', max_length=50, verbose_name='Pump Type'),
        ),
    ]
