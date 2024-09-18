# Generated by Django 5.0.6 on 2024-09-13 23:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_camviddata_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='camviddata',
            name='Classes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='camviddata',
            name='Quantity',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
    ]
