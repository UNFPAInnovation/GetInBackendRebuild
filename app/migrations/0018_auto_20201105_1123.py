# Generated by Django 2.2.8 on 2020-11-05 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20200904_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Married', 'Married'), ('Single', 'Single'), ('Divorced', 'Divorced')], default='Single', max_length=250),
        ),
        migrations.AlterField(
            model_name='msiservice',
            name='option',
            field=models.CharField(choices=[('AN1', 'AN1'), ('AN2', 'AN2'), ('AN3', 'AN3'), ('AN4', 'AN4'), ('Delivery', 'Delivery'), ('Family Planning', 'Family Planning')], default='AN1', max_length=250),
        ),
    ]