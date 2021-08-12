# Generated by Django 3.2.6 on 2021-08-10 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0002_temp_acciones_prestamos_temp_datos_prestamos'),
    ]

    operations = [
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='Monto',
            new_name='Intereses',
        ),
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='Recargos_mora',
            new_name='capital',
        ),
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='fecha_otorgado',
            new_name='fecha_cuota',
        ),
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='Periodo_Gracia',
            new_name='num_cuota',
        ),
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='Taza_Descuento',
            new_name='saldo',
        ),
        migrations.RenameField(
            model_name='temp_acciones_prestamos',
            old_name='taza_mensual',
            new_name='total_cuota',
        ),
        migrations.RemoveField(
            model_name='datos_prestamos',
            name='Recargos_mora',
        ),
        migrations.RemoveField(
            model_name='temp_acciones_prestamos',
            name='fecha_vencimiento',
        ),
        migrations.RemoveField(
            model_name='temp_acciones_prestamos',
            name='id_prestamo',
        ),
        migrations.RemoveField(
            model_name='temp_acciones_prestamos',
            name='nombre_cliente',
        ),
        migrations.RemoveField(
            model_name='temp_acciones_prestamos',
            name='plazo_meses',
        ),
        migrations.RemoveField(
            model_name='temp_datos_prestamos',
            name='Recargos_mora',
        ),
        migrations.RemoveField(
            model_name='temp_datos_prestamos',
            name='fecha_vencimiento',
        ),
    ]