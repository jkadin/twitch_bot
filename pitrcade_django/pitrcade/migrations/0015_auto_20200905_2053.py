# Generated by Django 2.1.15 on 2020-09-06 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pitrcade', '0014_auto_20200708_0111'),
    ]

    operations = [
        migrations.AddField(
            model_name='configsetting',
            name='multiball_alert_duration',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='gameresultmessage',
            name='image_or_video_alert_multiball_url',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='gameresultmessage',
            name='sound_alert_multiball_url',
            field=models.TextField(blank=True),
        ),
    ]
