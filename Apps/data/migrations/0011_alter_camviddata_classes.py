# Generated by Django 5.0.6 on 2024-09-13 23:49

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_alter_camviddata_classes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camviddata',
            name='Classes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[(0, 'Mariposa 1'), (1, 'Mariposa 2'), (2, 'Mariposa 3'), (3, 'Mariposa 4')], max_length=3, verbose_name='Clases'), blank=True, null=True, size=None),
        ),
    ]
