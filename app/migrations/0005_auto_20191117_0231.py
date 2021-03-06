# Generated by Django 2.2.6 on 2019-11-17 02:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20191116_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Single', 'Single'), ('Divorced', 'Divorced'), ('Married', 'Married')], default='Single', max_length=250),
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('Before', 'Before'), ('After', 'After'), ('Current', 'Current')], default='After', max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Appointment')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
