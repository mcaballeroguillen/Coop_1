# Generated by Django 3.2.6 on 2021-10-11 20:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0010_auto_20211010_1811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventario',
            name='Fecha_Ingreso',
            field=models.DateField(default=datetime.datetime(2021, 10, 11, 20, 41, 53, 620203, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='temp_inventario',
            name='Fecha_Ingreso',
            field=models.DateField(default=datetime.datetime(2021, 10, 11, 20, 41, 53, 620645, tzinfo=utc)),
        ),
    ]
