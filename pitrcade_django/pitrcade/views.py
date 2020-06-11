from django.views import generic
from django.apps import apps
from django.utils import timezone
from django.db import IntegrityError
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Player
from preferences import preferences

class ScoreboardView(generic.ListView):
    template_name = 'pitrcade/scoreboard.html'
    context_object_name = 'player_list'

    def get_queryset(self):
        """Return the top x players by score"""
        top_scores = preferences.ConfigSetting.scoreboard_number_of_top_scores
        return Player.objects.order_by('-score')[:top_scores]

    def get_context_data(self, **kwargs):
        context = super(ScoreboardView, self).get_context_data(**kwargs)
        context['json_player_list'] = serializers.serialize('json', context['player_list'], fields=('username', 'score'))
        context['game_title'] = preferences.ConfigSetting.game_title
        context['scoreboard_refresh'] = preferences.ConfigSetting.scoreboard_refresh_seconds
        return context

    def render_to_response(self, context, **response_kwargs):
        """Override to add json response if ajax, otherwise load template as normal"""
        if self.request.is_ajax():
            return HttpResponse(context['json_player_list'], content_type='application/json')
        else:
            return super(ScoreboardView, self).render_to_response(context, **response_kwargs)
