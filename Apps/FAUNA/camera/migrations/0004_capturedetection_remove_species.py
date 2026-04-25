import django.db.models.deletion
from django.db import migrations, models


def migrate_detections(apps, schema_editor):
    CameraCapture = apps.get_model('camera', 'CameraCapture')
    CaptureDetection = apps.get_model('camera', 'CaptureDetection')
    for cap in CameraCapture.objects.all():
        species = getattr(cap, 'Species', None)
        count = getattr(cap, 'SpeciesCount', 1) or 1
        if species:
            CaptureDetection.objects.create(Capture=cap, Species=species, Count=count)


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0003_camerastation_macaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaptureDetection',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('Species', models.CharField(max_length=200, verbose_name='Species / Class')),
                ('Count', models.PositiveIntegerField(default=1, verbose_name='Count')),
                ('Capture', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='detections',
                    to='camera.cameracapture',
                    verbose_name='Capture',
                )),
            ],
            options={'verbose_name': 'Detection', 'verbose_name_plural': 'Detections'},
        ),
        migrations.RunPython(migrate_detections, migrations.RunPython.noop),
        migrations.RemoveField(model_name='cameracapture', name='Species'),
        migrations.RemoveField(model_name='cameracapture', name='SpeciesCount'),
    ]
