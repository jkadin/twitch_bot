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

    def insert_quarter(self, num_plays):
        best_points = 0
        results = []
        game_title = preferences.ConfigSetting.game_title
        for i in range(1, num_plays + 1):
            self.num_quarters += 1
            points = self.generate_random_score()
            history = GameResultHistory(player=self, score=points)
            history.save()
            game_results = GameResultMessage.objects.filter(score__in=[-1, points])
            game_results = game_results.order_by('-score')
            result_message = game_results.values_list('message', flat=True)[0]

            if num_plays > 1:
                alert_video = game_results.values_list('image_or_video_alert_url', flat=True)[0] or 'http://'
                alert_duration = preferences.ConfigSetting.alert_duration*1000
            else:
                alert_video = game_results.values_list('image_or_video_alert_multiball_url', flat=True)[0] or 'http://'
                alert_duration = preferences.ConfigSetting.multiball_alert_duration*1000
            if i > 1:
                alert_audio = game_results.values_list('sound_alert_multiball_url', flat=True)[0] or 'http://'
            else:
                alert_audio = game_results.values_list('sound_alert_url', flat=True)[0] or 'http://'

            results.append({'message': result_message.format(username=self.username, score=points, total_score=self.score, game_title=game_title),
                            'image_or_video_alert_url': alert_video,
                            'sound_alert_url': alert_audio,
                            'alert_duration': alert_duration,
                            })
            if points > best_points:
                best_points = points
        # self.score += points
        # Changing to non-cumulative score per Pitr's request
        if best_points > self.score:
            self.score = best_points
            self.save()
        return results

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


class GameResultHistory(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)


class GameResultMessage(models.Model):
    score = models.IntegerField(default=-1, unique=True)
    message = models.TextField(blank=True)
    image_or_video_alert_url = models.TextField(blank=True)
    sound_alert_url = models.TextField(blank=True)
    image_or_video_alert_multiball_url = models.TextField(blank=True)
    sound_alert_multiball_url = models.TextField(blank=True)

    def __str__(self):
        return f'{self.score}'


class ConfigSetting(Preferences):
    game_title = models.CharField(max_length=50)
    alert_duration = models.IntegerField(default=3)
    multiball_alert_duration = models.IntegerField(default=1)
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=1000)
    normal_score_distribution = models.BooleanField(default=True)
    scoreboard_refresh_seconds = models.IntegerField(default=15)
    scoreboard_number_of_top_scores = models.IntegerField(default=10)
    scoreboard_title_color = ColorField(default='#FFFF00') # Default: yellow
    scoreboard_header_color = ColorField(default='#FF0000') # Default: red
    scoreboard_player_color = ColorField(default='#0000FF') # Default: blue
    scoreboard_next_player_reset = models.DateTimeField(default=timezone.make_aware(datetime.datetime.fromtimestamp(0)))
    scoreboard_player_reset_interval = models.DurationField(default=datetime.timedelta(weeks=1))
    streamlabs_access_token = models.TextField(default="")


class PremadePoll(models.Model):
    title = models.CharField(max_length=100, unique=True)
    options = models.TextField()
    multi = models.BooleanField(default=False)


class PollerbotData(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.key}: {self.value}'
