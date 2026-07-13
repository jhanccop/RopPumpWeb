from django.db import migrations


def create_applications(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    apps_data = [
        {
            'Code': 'transformadores',
            'Name': 'Transformadores',
            'Description': 'Gestión de transformadores eléctricos',
            'Icon': 'fas fa-bolt',
            'DashboardUrl': '/transformer/',
            'IsActive': True,
        },
        {
            'Code': 'fauna',
            'Name': 'Fauna',
            'Description': 'Monitoreo de fauna silvestre con cámaras trampa',
            'Icon': 'fas fa-leaf',
            'DashboardUrl': '/camera/dashboard/',
            'IsActive': True,
        },
        {
            'Code': 'oilfield',
            'Name': 'Oilfield',
            'Description': 'Monitoreo y gestión de campos petroleros',
            'Icon': 'fas fa-industry',
            'DashboardUrl': '/oilfield/',
            'IsActive': True,
        },
    ]
    for data in apps_data:
        Application.objects.get_or_create(Code=data['Code'], defaults=data)


def remove_applications(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    Application.objects.filter(Code__in=['transformadores', 'fauna', 'oilfield']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_application_user_isactive_alter_user_role_and_more'),
    ]

    operations = [
        migrations.RunPython(create_applications, remove_applications),
    ]
