# Generated by Django 3.2.6 on 2021-08-12 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0008_alter_datos_prestamos_id_cliente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variables_Generales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=50)),
                ('valor', models.CharField(max_length=50)),
            ],
        ),
    ]