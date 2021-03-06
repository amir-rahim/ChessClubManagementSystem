# Generated by Django 3.2.5 on 2021-11-25 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0021_alter_tournament_club'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='organizer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
