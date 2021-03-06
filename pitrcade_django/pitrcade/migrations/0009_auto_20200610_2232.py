# Generated by Django 2.1.15 on 2020-06-11 05:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pitrcade', '0008_auto_20200610_2228'),
    ]

    operations = [
        migrations.RenameField(
            model_name='configsetting',
            old_name='normal_distribution_score',
            new_name='normal_score_distribution',
        ),
        migrations.RenameField(
            model_name='configsetting',
            old_name='scoreboard_top_scores',
            new_name='scoreboard_number_of_top_scores',
        ),
        migrations.RenameField(
            model_name='configsetting',
            old_name='scoreboard_refresh',
            new_name='scoreboard_refresh_seconds',
        ),
        migrations.AlterField(
            model_name='configsetting',
            name='scoreboard_next_player_reset',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 17, 22, 32, 31, 468412)),
        ),
    ]
