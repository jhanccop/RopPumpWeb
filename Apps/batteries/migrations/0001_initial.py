# Generated by Django 4.2.1 on 2023-09-26 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateCreated', models.DateTimeField(auto_now_add=True)),
                ('BatteryName', models.CharField(blank=True, max_length=100, unique=True, verbose_name='Battery Name')),
                ('Company', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='company.company')),
            ],
            options={
                'verbose_name': 'Battery',
                'verbose_name_plural': 'Batteries',
            },
        ),
    ]
