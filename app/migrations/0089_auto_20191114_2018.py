# Generated by Django 2.2.6 on 2019-11-14 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0088_auto_20191114_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointmentencounter',
            name='bleeding_heavily',
        ),
        migrations.RemoveField(
            model_name='appointmentencounter',
            name='blurred_vision',
        ),
        migrations.RemoveField(
            model_name='appointmentencounter',
            name='fever',
        ),
        migrations.RemoveField(
            model_name='appointmentencounter',
            name='swollen_feet',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='family_planning_type',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='followup_reason',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='no_family_planning_reason',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='using_family_planning',
        ),
        migrations.RemoveField(
            model_name='followup',
            name='bleeding_heavily',
        ),
        migrations.RemoveField(
            model_name='followup',
            name='blurred_vision',
        ),
        migrations.RemoveField(
            model_name='followup',
            name='fever',
        ),
        migrations.RemoveField(
            model_name='followup',
            name='followup_reason',
        ),
        migrations.RemoveField(
            model_name='followup',
            name='swollen_feet',
        ),
        migrations.AddField(
            model_name='appointmentencounter',
            name='appointment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Appointment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointmentencounter',
            name='observation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.Observation'),
        ),
        migrations.AddField(
            model_name='delivery',
            name='family_planning',
            field=models.ManyToManyField(blank=True, null=True, to='app.FamilyPlanning'),
        ),
        migrations.AddField(
            model_name='followup',
            name='observation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.Observation'),
        ),
        migrations.AlterField(
            model_name='girl',
            name='marital_status',
            field=models.CharField(choices=[('Divorced', 'Divorced'), ('Single', 'Single'), ('Married', 'Married')], default='Single', max_length=250),
        ),
        migrations.AlterField(
            model_name='mappingencounter',
            name='family_planning',
            field=models.ManyToManyField(blank=True, null=True, to='app.FamilyPlanning'),
        ),
        migrations.AlterField(
            model_name='mappingencounter',
            name='observation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.Observation'),
        ),
    ]