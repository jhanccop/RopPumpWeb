# Generated by Django 5.0.6 on 2024-06-22 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0008_rename_datecreate_tank_created_at_tank_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tank',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='tank',
            name='updated_at',
        ),
    ]
