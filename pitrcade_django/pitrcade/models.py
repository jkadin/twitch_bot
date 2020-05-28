from django.db import models
import random


class Player(models.Model):
    username = models.CharField(max_length=50, unique=True)
    num_quarters = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def insert_quarter(self):
        self.num_quarters += 1
        points = self.generate_random_score()
        self.score += points
        game_results = GameResult.objects.filter(max_score__lte=points)
        game_results = game_results.order_by('max_score').desc()
        result_message = game_results.values_list('message', flat=True)[0]
        return result_message

    def generate_random_score(self):
        return random.randint(0, 1000)

    def __str__(self):
        return f'{self.username}'


class GameResult(models.Model):
    max_score = models.IntegerField(default=0, unique=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f'{self.max_score}'


class ConfigurationSetting(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.key}: {self.value}'
