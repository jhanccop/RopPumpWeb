# Generated by Django 4.2.1 on 2023-10-17 02:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
        ('wells', '0003_alter_well_refresh'),
    ]

    operations = [
        migrations.CreateModel(
            name='tank',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('DateCreate', models.DateTimeField(auto_now_add=True)),
                ('TankName', models.CharField(max_length=100, unique=True, verbose_name='Tank Name')),
                ('TankHeight', models.FloatField(blank=True, null=True, verbose_name='Tank Height')),
                ('TankFactor', models.FloatField(blank=True, null=True, verbose_name='Tank Factor')),
                ('Refresh', models.FloatField(blank=True, choices=[(30, '30s'), (60, '1m'), (120, '2m'), (300, '5m'), (600, '10m'), (900, '15m'), (1800, '30m')], default=120, null=True, verbose_name='Refresh')),
                ('GroupName', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.group')),
            ],
            options={
                'verbose_name': 'tank',
                'verbose_name_plural': 'tanks',
            },
        ),
    ]
