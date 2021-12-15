# Generated by Django 3.2.5 on 2021-12-14 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0043_user_elo_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='elo_rating',
            new_name='current_elo_rating',
        ),
        migrations.AddField(
            model_name='user',
            name='highest_elo_rating',
            field=models.IntegerField(default=1000),
        ),
        migrations.AddField(
            model_name='user',
            name='lowest_elo_rating',
            field=models.IntegerField(default=1000),
        ),
    ]
