# Generated by Django 3.2.6 on 2021-10-10 17:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0008_auto_20210920_0213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventario',
            name='Fecha_Ingreso',
            field=models.DateField(default=datetime.datetime(2021, 10, 10, 17, 50, 5, 59913, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='temp_inventario',
            name='Fecha_Ingreso',
            field=models.DateField(default=datetime.datetime(2021, 10, 10, 17, 50, 5, 60286, tzinfo=utc)),
        ),
    ]