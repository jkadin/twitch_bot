import django_tables2 as tables
from .models import GameResultHistory

class GameResultHistoryTable(tables.Table):
    class Meta:
        model = GameResultHistory
        fields = ['player', 'score', 'datetime']
        order_by = '-datetime'
        template_name = "django_tables2/semantic.html"
