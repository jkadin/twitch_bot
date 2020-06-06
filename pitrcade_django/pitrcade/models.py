from django.db import models
import random


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
        game_title = ConfigurationSetting.objects.get(key='Game Title').value
        game_results = GameResult.objects.filter(min_score__lte=points)
        game_results = game_results.order_by('-min_score')
        result_message = game_results.values_list('message', flat=True)[0]
        return result_message.format(username=self.username, score=points, total_score=self.score, game_title=game_title)

    def generate_random_score(self):
        try:
            min_score = int(ConfigurationSetting.objects.get(key='Minimum points per donation').value)
        except:
            min_score = 0

        try:
            max_score = int(ConfigurationSetting.objects.get(key='Maximum points per donation').value)
        except:
            max_score = 1000
        return random.randint(min_score, max_score)

    def __str__(self):
        return f'{self.username}'


class GameResult(models.Model):
    min_score = models.IntegerField(default=0, unique=False)
    message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.min_score}'


class ConfigurationSetting(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.key}: {self.value}'


class PollerbotData(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.key}: {self.value}'
