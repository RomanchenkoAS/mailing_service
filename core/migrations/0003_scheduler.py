# Generated by Django 5.0.3 on 2024-03-09 13:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_footer_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='daily', max_length=10)),
                ('time_of_day', models.TimeField(help_text='Time of day to send the emails (HH:MM:SS format).')),
            ],
        ),
        migrations.AlterField(
            model_name='dispatch',
            name='footer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dispatch', to='core.footer'),
        ),
        migrations.AlterField(
            model_name='dispatch',
            name='last_sent_at',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='footer',
            name='text',
            field=models.CharField(blank=True, help_text='Email footer text.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='footer',
            name='title',
            field=models.CharField(help_text='Identifier, is not included into email.', max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='dispatch',
            name='scheduler',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispatches', to='core.scheduler'),
        ),
    ]
