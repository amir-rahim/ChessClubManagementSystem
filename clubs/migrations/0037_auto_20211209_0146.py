# Generated by Django 3.2.5 on 2021-12-09 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0036_tournament_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='stage',
            field=models.CharField(choices=[('S', 'Signup'), ('E', 'Elimination'), ('G', 'Group Stages')], default='E', max_length=1),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='stage',
            field=models.CharField(choices=[('S', 'Signup'), ('E', 'Elimination'), ('G', 'Group Stages')], default='S', max_length=1),
        ),
    ]
