# Generated by Django 3.2.5 on 2021-12-14 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0042_merge_20211212_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='elo_rating',
            field=models.IntegerField(default=1000),
        ),
    ]
