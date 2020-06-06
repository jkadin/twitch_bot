from django.core.management.base import BaseCommand, CommandError
from .models import Player, ConfigurationSetting
import datetime

class Command(BaseCommand):
    help = 'Reset the scoreboard for the week'

    def handle(self, *args, **options):
        reset_obj = ConfigurationSetting.objects.get(key='Player Reset Datetime')
        reset_datetime = datetime.datetime.fromisoformat(reset_onj.value)
        now = datetime.datetime.now()
        if now => reset_datetime:
            Player.objects.all().delete()
            reset_obj.value = (reset_datetime + datetime.timedelta(weeks=1)).isoformat()
            reset_obj.save()
