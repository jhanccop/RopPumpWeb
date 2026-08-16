from django.db import migrations


def add_seguridad(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    Application.objects.get_or_create(
        Code='seguridad',
        defaults={
            'Name': 'Seguridad',
            'Description': 'Sistema de seguridad de ambiente controlado',
            'Icon': 'fas fa-shield-alt',
            'DashboardUrl': '/seguridad/',
            'IsActive': True,
        },
    )


def remove_seguridad(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    Application.objects.filter(Code='seguridad').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_initial_applications'),
    ]

    operations = [
        migrations.RunPython(add_seguridad, remove_seguridad),
    ]
