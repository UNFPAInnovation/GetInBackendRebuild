# Generated by Django 2.2.6 on 2019-11-05 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_auto_20191105_0749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointmentencounter',
            name='risks_identified',
        ),
        migrations.AddField(
            model_name='appointmentencounter',
            name='used_ambulance',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Divorced', 'Divorced'), ('Single', 'Single'), ('Married', 'Married')], default='Single', max_length=250),
        ),
    ]
