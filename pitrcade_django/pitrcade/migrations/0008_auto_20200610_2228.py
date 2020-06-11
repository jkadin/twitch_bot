# Generated by Django 2.1.15 on 2020-06-11 05:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pitrcade', '0007_auto_20200610_2226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configsetting',
            name='max_score',
            field=models.IntegerField(default=1000),
        ),
        migrations.AlterField(
            model_name='configsetting',
            name='min_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='configsetting',
            name='scoreboard_next_player_reset',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 17, 22, 28, 24, 584028)),
        ),
    ]