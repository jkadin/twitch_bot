# Generated by Django 2.1.15 on 2020-06-11 06:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('pitrcade', '0010_auto_20200610_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configsetting',
            name='scoreboard_next_player_reset',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 18, 6, 34, 26, 874353, tzinfo=utc)),
        ),
    ]
