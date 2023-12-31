# Generated by Django 4.2.1 on 2023-10-16 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0003_alter_well_refresh'),
        ('overview', '0004_alter_rodpumpdata_tanklevel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TankData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TankName', models.CharField(blank=True, max_length=20, null=True, verbose_name='Tank Name')),
                ('DateCreate', models.DateTimeField(auto_now_add=True)),
                ('Status', models.CharField(blank=True, max_length=20, null=True, verbose_name='Status')),
                ('OilLevel', models.FloatField(blank=True, null=True, verbose_name='Oil Level')),
                ('WaterLevel', models.FloatField(blank=True, null=True, verbose_name='Water Level')),
                ('PumpName', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wells.well')),
            ],
            options={
                'verbose_name': 'Tank Data',
                'verbose_name_plural': 'All Tank Data',
            },
        ),
    ]
