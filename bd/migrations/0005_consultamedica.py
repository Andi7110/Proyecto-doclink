# Generated by Django 5.2.3 on 2025-06-16 21:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bd', '0004_alter_citasmedicas_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultaMedica',
            fields=[
                ('id_consulta_medica', models.BigAutoField(primary_key=True, serialize=False)),
                ('sintomas', models.TextField(blank=True, null=True)),
                ('diagnostico', models.TextField(blank=True, null=True)),
                ('tratamiento', models.TextField(blank=True, null=True)),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('documentos_adjuntos', models.FileField(blank=True, null=True, upload_to='consultas/documentos/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fk_cita', models.OneToOneField(db_column='fk_cita', on_delete=django.db.models.deletion.CASCADE, related_name='consulta_medica', to='bd.citasmedicas')),
            ],
            options={
                'db_table': 'consulta_medica',
                'managed': True,
            },
        ),
    ]
