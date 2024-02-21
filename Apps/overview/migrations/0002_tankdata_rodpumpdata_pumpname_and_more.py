# Generated by Django 4.2.1 on 2024-01-18 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0001_initial'),
        ('overview', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TankData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateCreate', models.DateTimeField(auto_now_add=True)),
                ('Status', models.CharField(blank=True, max_length=20, null=True, verbose_name='Status')),
                ('OilLevel', models.FloatField(blank=True, null=True, verbose_name='Oil Level')),
                ('WaterLevel', models.FloatField(blank=True, null=True, verbose_name='Water Level')),
                ('Temperature', models.FloatField(blank=True, null=True, verbose_name='Temperature')),
            ],
            options={
                'verbose_name': 'Tank Data',
                'verbose_name_plural': 'All Tank Data',
            },
        ),
        migrations.AddField(
            model_name='rodpumpdata',
            name='PumpName',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wells.well'),
        ),
        migrations.AddField(
            model_name='rodpumpdata',
            name='RawSurfaceLoad',
            field=models.TextField(blank=True, null=True, verbose_name='Raw Surf Load'),
        ),
        migrations.AddField(
            model_name='rodpumpdata',
            name='RawSurfacePosition',
            field=models.TextField(blank=True, null=True, verbose_name='Raw Surf Position'),
        ),
        migrations.AddField(
            model_name='rodpumpdata',
            name='TankLevel',
            field=models.FloatField(blank=True, null=True, verbose_name='Tank Level'),
        ),
        migrations.AlterField(
            model_name='rodpumpdata',
            name='Status',
            field=models.CharField(blank=True, choices=[('Normal running', 'Normal running'), ('Stopped unit', 'Stopped unit')], max_length=100, null=True, verbose_name='Status'),
        ),
    ]