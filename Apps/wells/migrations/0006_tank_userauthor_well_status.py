# Generated by Django 4.2.1 on 2023-10-28 10:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wells', '0005_tank_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='tank',
            name='UserAuthor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='well',
            name='Status',
            field=models.CharField(choices=[('stopped', 'stopped'), ('running', 'running'), ('low battery', 'low battery'), ('no signal', 'no signal'), ('not synchronized', 'not synchronized')], default='stopped', max_length=50, verbose_name='Status'),
        ),
    ]
