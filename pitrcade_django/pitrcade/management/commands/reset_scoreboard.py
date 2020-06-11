from django.core.management.base import BaseCommand, CommandError
from pitrcade.models import Player, ConfigurationSetting
from preferences import preferences
from django.utils import timezone

class Command(BaseCommand):
    help = 'Reset the scoreboard for the week'

    def handle(self, *args, **options):
        reset_datetime = preferences.ConfigSetting.scoreboard_next_player_reset
        now = timezone.now()
        if now >= reset_datetime:
            Player.objects.all().delete()
            reset_datetime = (reset_datetime + preferences.ConfigSetting.scoreboard_player_reset_interval)
            preferences.ConfigSetting.save()
