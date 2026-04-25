from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0004_capturedetection_remove_species'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpeciesLabel',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ClassId', models.PositiveIntegerField(unique=True, verbose_name='Class ID')),
                ('Name', models.CharField(max_length=200, unique=True, verbose_name='Species Name')),
                ('Description', models.TextField(blank=True, default='', verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Species / Class Label',
                'verbose_name_plural': 'Species / Class Labels',
                'ordering': ['ClassId'],
            },
        ),
    ]
