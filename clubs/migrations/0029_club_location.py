# Generated by Django 3.2.5 on 2021-12-01 16:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0028_auto_20211201_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='location',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
