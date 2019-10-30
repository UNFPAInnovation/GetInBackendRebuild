# Generated by Django 2.2.6 on 2019-10-25 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20191025_1300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mappingencounter',
            name='bleeding_heavily',
        ),
        migrations.AddField(
            model_name='mappingencounter',
            name='bleeding',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')], default='single', max_length=250),
        ),
    ]