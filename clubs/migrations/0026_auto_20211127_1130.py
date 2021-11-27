# Generated by Django 3.2.5 on 2021-11-27 11:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0025_auto_20211125_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='name',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='Club name must start with a letter and contain only letters, number, and spaces.', regex='[a-zA-Z ][a-zA-Z0-9 ]+')]),
        ),
        migrations.AlterField(
            model_name='membership',
            name='club',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='clubs.club'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
