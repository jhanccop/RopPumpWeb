# Generated by Django 4.2.1 on 2023-09-26 19:37

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RodPumpData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateCreate', models.DateTimeField(auto_now_add=True)),
                ('SurfaceLoad', models.TextField(blank=True, null=True, verbose_name='Surf Load')),
                ('SurfacePosition', models.TextField(blank=True, null=True, verbose_name='Surf Position')),
                ('DownLoad', models.TextField(blank=True, null=True, verbose_name='Down Load')),
                ('DownPosition', models.TextField(blank=True, null=True, verbose_name='Down Position')),
                ('RunTime', models.FloatField(blank=True, null=True, verbose_name='Run Time')),
                ('RawAcceleration', models.TextField(blank=True, null=True, verbose_name='RawAcceleration')),
                ('TubingPressure', models.FloatField(blank=True, null=True, verbose_name='Tubing Pressure')),
                ('CasingPressure', models.FloatField(blank=True, null=True, verbose_name='Casing Pressure')),
                ('SPM', models.FloatField(blank=True, null=True, verbose_name='SPM')),
                ('Status', models.CharField(blank=True, max_length=20, null=True, verbose_name='Status')),
                ('Diagnosis', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('None', 'None'), ('Full pump', 'Full pump'), ('Leak travel valve', 'Leak travel valve'), ('Leak standing valve', 'Leak standing valve'), ('Worn pump barrel', 'Worn pump barrel'), ('Light fluid stroke', 'Light fluid stroke'), ('Medium fluid stroke', 'Medium fluid stroke'), ('Severe fluid stroke', 'Severe fluid stroke'), ('Gas interference', 'Gas interference'), ('Shock of pump up', 'Shock of pump up'), ('Shock of pump down', 'Shock of pump down'), ('Recovering level', 'Recovering level'), ('Rods broken', 'Rods broken')], max_length=100, null=True, verbose_name='Diagnosis')),
                ('PumpFill', models.FloatField(blank=True, null=True, verbose_name='Pump Fill')),
                ('Recomendation', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Good work area', 'Good work area'), ('Schedule to workover', 'Schedule to workover'), ('Unit re-spacing', 'Unit re-spacing'), ('Reduce strokes per minute', 'Reduce strokes per minute'), ('Stop pump unit', 'Stop pump unit')], max_length=100, null=True, verbose_name='Recomendation')),
            ],
            options={
                'verbose_name': 'Socker Rod Pump Data',
                'verbose_name_plural': 'All Socker Rod Pump Data',
            },
        ),
    ]
