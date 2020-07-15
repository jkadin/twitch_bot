from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name='pitrcade'

urlpatterns = [
#Add index with links to admin or scoreboard
    path('scoreboard', views.ScoreboardView.as_view(), name='scoreboard'),
    path('scoreboard/overlay', views.ScoreboardViewForOverlay.as_view(), name='scoreboard_overlay'),
    path('history', views.GameResultHistory.as_view(), name='history'),
    path('streamlabs', views.StreamlabsAuthView.as_view(), name='streamlabs'),
    path('', RedirectView.as_view(pattern_name='pitrcade:scoreboard')),
]
