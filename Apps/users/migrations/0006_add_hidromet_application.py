from django.db import migrations, models


def add_hidromet(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    Application.objects.get_or_create(
        Code='hidromet',
        defaults={
            'Name': 'Hidrometeorología',
            'Description': 'Red de estaciones hidrometeorológicas (ríos, cuencas y quebradas)',
            'Icon': 'fas fa-water',
            'DashboardUrl': '/hidromet/',
            'IsActive': True,
        },
    )


def remove_hidromet(apps, schema_editor):
    Application = apps.get_model('users', 'Application')
    Application.objects.filter(Code='hidromet').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_application_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='Code',
            field=models.CharField(choices=[('transformadores', 'Transformadores'), ('fauna', 'Fauna'), ('oilfield', 'Oilfield'), ('seguridad', 'Seguridad'), ('hidromet', 'Hidrometeorología')], max_length=50, unique=True, verbose_name='Código'),
        ),
        migrations.RunPython(add_hidromet, remove_hidromet),
    ]
