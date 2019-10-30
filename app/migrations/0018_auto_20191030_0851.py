# Generated by Django 2.2.6 on 2019-10-30 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20191030_0839'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='is_baby_alive',
            new_name='baby_alive',
        ),
        migrations.RenameField(
            model_name='delivery',
            old_name='is_mother_alive',
            new_name='mother_alive',
        ),
        migrations.RenameField(
            model_name='delivery',
            old_name='received_postnatal_care',
            new_name='postnatal_care',
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('divorced', 'Divorced'), ('married', 'Married'), ('single', 'Single')], default='single', max_length=250),
        ),
    ]
