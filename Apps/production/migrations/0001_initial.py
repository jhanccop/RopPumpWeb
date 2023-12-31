# Generated by Django 4.2.1 on 2023-09-26 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionFluid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DateCreate', models.DateTimeField(auto_now_add=True)),
                ('OilProd', models.FloatField(blank=True, null=True, verbose_name='Oil Production')),
                ('WaterProd', models.FloatField(blank=True, null=True, verbose_name='Water Production')),
                ('DateTest', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Production',
                'verbose_name_plural': 'All production',
            },
        ),
    ]
