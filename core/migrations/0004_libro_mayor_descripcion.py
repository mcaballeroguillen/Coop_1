# Generated by Django 3.2.6 on 2021-09-20 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210919_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='libro_mayor',
            name='Descripcion',
            field=models.CharField(default='s', max_length=100),
            preserve_default=False,
        ),
    ]
