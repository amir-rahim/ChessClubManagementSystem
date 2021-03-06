# Generated by Django 3.2.5 on 2021-12-14 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0044_auto_20211214_1853'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='result',
            new_name='_result',
        ),
        migrations.RemoveField(
            model_name='user',
            name='current_elo_rating',
        ),
        migrations.RemoveField(
            model_name='user',
            name='draw',
        ),
        migrations.RemoveField(
            model_name='user',
            name='highest_elo_rating',
        ),
        migrations.RemoveField(
            model_name='user',
            name='loss',
        ),
        migrations.RemoveField(
            model_name='user',
            name='lowest_elo_rating',
        ),
        migrations.RemoveField(
            model_name='user',
            name='win',
        ),
        migrations.AddField(
            model_name='match',
            name='result_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
