# Generated by Django 2.2.8 on 2021-10-28 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20211028_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Single', 'Single'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed'), ('Married', 'Married')], default='Single', max_length=250),
        ),
    ]
