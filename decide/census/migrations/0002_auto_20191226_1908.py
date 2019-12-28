# Generated by Django 2.0.10 on 2019-12-26 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='census',
            name='fecha_nacimiento',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='census',
            name='genero',
            field=models.CharField(choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='census',
            name='localidad',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='census',
            name='provincia',
            field=models.CharField(max_length=20, null=True),
        ),
    ]