from django.db import models
import random
import datetime
from django.utils import timezone
from colorfield.fields import ColorField
from preferences.models import Preferences
from preferences import preferences


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    num_quarters = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def insert_quarter(self):
        self.num_quarters += 1
        points = self.generate_random_score()
        # self.score += points
        # Changing to non-cumulative score per Pitr's request
        if points > self.score:
            self.score = points
            self.save()
        game_title = preferences.ConfigSetting.game_title
        game_results = GameResult.objects.filter(min_score__lte=points)
        game_results = game_results.order_by('-min_score')
        result_message = game_results.values_list('message', flat=True)[0]
        return result_message.format(username=self.username, score=points, total_score=self.score, game_title=game_title)

    def generate_random_score(self):
        min_score = preferences.ConfigSetting.min_score
        max_score = preferences.ConfigSetting.max_score

        if preferences.ConfigSetting.normal_score_distribution:
            result = int(random.normalvariate((max_score-min_score)/2, (max_score-min_score)/2/3) + min_score)
            while not min_score <= result <= max_score:
                result = int(random.normalvariate((max_score-min_score)/2, (max_score-min_score)/2/3) + min_score)
        else:
            result = random.randint(min_score, max_score)
        return result

    def __str__(self):
        return f'{self.username}'


class GameResult(models.Model):
    min_score = models.IntegerField(default=0, unique=False)
    message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.min_score}'


class ConfigSetting(Preferences):
    game_title = models.CharField(max_length=50)
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=1000)
    normal_score_distribution = models.BooleanField(default=True)
    scoreboard_refresh_seconds = models.IntegerField(default=15)
    scoreboard_number_of_top_scores = models.IntegerField(default=10)
    scoreboard_title_color = ColorField(default='#FFFF00') # Default: yellow
    scoreboard_header_color = ColorField(default='#FF0000') # Default: red
    scoreboard_player_color = ColorField(default='#0000FF') # Default: blue
    scoreboard_next_player_reset = models.DateTimeField(default=timezone.now() + datetime.timedelta(weeks=1))
    scoreboard_player_reset_interval = models.DurationField(default=datetime.timedelta(weeks=1))


class PollerbotData(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.key}: {self.value}'
