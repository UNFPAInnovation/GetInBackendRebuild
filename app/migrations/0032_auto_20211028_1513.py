# Generated by Django 2.2.8 on 2021-10-28 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20211028_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='girl',
            name='disability',
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Divorced', 'Divorced'), ('Married', 'Married'), ('Single', 'Single'), ('Widowed', 'Widowed')], default='Single', max_length=250),
        ),
    ]
