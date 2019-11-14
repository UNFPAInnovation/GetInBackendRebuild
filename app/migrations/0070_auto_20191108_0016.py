# Generated by Django 2.2.6 on 2019-11-08 00:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0069_auto_20191107_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='midwife',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Single', 'Single'), ('Divorced', 'Divorced'), ('Married', 'Married')], default='Single', max_length=250),
        ),
    ]