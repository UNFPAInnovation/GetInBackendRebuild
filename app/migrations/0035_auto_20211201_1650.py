# Generated by Django 2.2.8 on 2021-12-01 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20211105_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Divorced', 'Divorced'), ('Married', 'Married'), ('Single', 'Single'), ('Widowed', 'Widowed')], default='Single', max_length=250),
        ),
    ]
