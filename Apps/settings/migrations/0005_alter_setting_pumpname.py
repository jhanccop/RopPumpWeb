# Generated by Django 4.2.1 on 2023-10-04 02:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wells', '0001_initial'),
        ('settings', '0004_setting_devicetype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='PumpName',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wells.well'),
        ),
    ]
