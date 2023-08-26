# Generated by Django 4.2.1 on 2023-08-24 07:14

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('overview', '0003_remove_rodpumpdata_chokeopening'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rodpumpdata',
            name='Diagnosis',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('None', 'None'), ('Full pump', 'Full pump'), ('Leak travel valve', 'Leak travel valve'), ('Leak standing valve', 'Leak standing valve'), ('Worn pump barrel', 'Worn pump barrel'), ('Light fluid stroke', 'Light fluid stroke'), ('Medium fluid stroke', 'Medium fluid stroke'), ('Severe fluid stroke', 'Severe fluid stroke'), ('Gas interference', 'Gas interference'), ('Shock of pump up', 'Shock of pump up'), ('Shock of pump down', 'Shock of pump down'), ('Recovering level', 'Recovering level'), ('Rods broken', 'Rods broken')], max_length=100, null=True, verbose_name='Diagnosis'),
        ),
    ]
