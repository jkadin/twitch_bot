from django.views import generic
from django.apps import apps
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.db import IntegrityError
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django_tables2 import SingleTableView
from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
load_dotenv()

from .models import Player, ConfigSetting, GameResultHistory
from .tables import GameResultHistoryTable
from preferences import preferences

SL_API_URL = 'https://www.streamlabs.com/api/v1.0'
SL_CLIENT_ID = os.getenv('STREAMLABS_CLIENT_ID')
SL_CLIENT_SECRET = os.getenv('STREAMLABS_CLIENT_SECRET')

if os.getenv('DEBUG'):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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


class GameResultHistory(SingleTableView):
    model = GameResultHistory
    table_class = GameResultHistoryTable
    template_name = 'pitrcade/gamehistory.html'
    table_pagination = False


class StreamlabsAuthView(generic.View):
    def get(self, request, *args, **kwargs):
        if not 'code' in request.GET:
            print("doing the auth")
            redirect_uri='http://127.0.0.1:8000/accounts/streamlabs/'
            response_type='code'
            scope='alerts.create alerts.write donations.read donations.create'
            streamlabs = OAuth2Session(SL_CLIENT_ID, redirect_uri=redirect_uri, scope=scope)
            authorization_url, state = streamlabs.authorization_url(SL_API_URL + '/authorize')
            request.session['oauth_state'] = state
            return redirect(authorization_url)
        else:
            print('doing the callback')
            streamlabs = OAuth2Session(SL_CLIENT_ID, redirect_uri='http://127.0.0.1:8000/accounts/streamlabs/', state=request.session['oauth_state'])
            token = streamlabs.fetch_token(SL_API_URL + '/token',
                                            include_client_id=True,
                                            client_secret=SL_CLIENT_SECRET,
                                            authorization_response=request.get_full_path(),
                                            )
            cs = ConfigSetting.objects.get(pk=preferences.ConfigSetting.pk)
            cs.streamlabs_access_token = json.dumps(token)
            cs.save()
            return redirect('pitrcade:scoreboard')
