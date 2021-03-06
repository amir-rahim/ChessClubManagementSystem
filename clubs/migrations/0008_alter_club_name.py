# Generated by Django 3.2.5 on 2021-11-22 16:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0007_auto_20211122_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='name',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='Club name must consist of at least three alphanumericals', regex='[a-zA-Z]w')]),
        ),
    ]
