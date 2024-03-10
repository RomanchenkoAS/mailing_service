# Generated by Django 5.0.3 on 2024-03-10 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_scheduler'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='email',
            options={'get_latest_by': 'created_at', 'ordering': ['-created_at'], 'verbose_name': 'Email address', 'verbose_name_plural': 'Email addresses'},
        ),
        migrations.AddField(
            model_name='dispatch',
            name='next_due_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]