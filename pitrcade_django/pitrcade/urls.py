from django.urls import path

from . import views

app_name='pitrcade'

urlpatterns = [
#Add index with links to admin or scoreboard
    path('list/<str:model>', views.ListView.as_view(), name='list'),
    path('detail/<str:model>/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('scoreboard', views.ScoreboardView.as_view(), name='scoreboard'),
]
