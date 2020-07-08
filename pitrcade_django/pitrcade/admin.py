from django.contrib import admin
from preferences.admin import PreferencesAdmin
from django.contrib.auth.decorators import login_required
from preferences import preferences

from .models import Player, GameResultMessage, GameResultHistory, ConfigSetting, PremadePoll


admin.site.site_header = preferences.ConfigSetting.game_title
admin.site.site_title = preferences.ConfigSetting.game_title
admin.site.login = login_required(admin.site.login)


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Player Info', {'fields': ['username', 'score', 'num_quarters']}),
]
    list_display = ('username', 'score', 'num_quarters')
    search_fields = ['username']

admin.site.register(Player, PlayerAdmin)


class GameResultMessageAdmin(admin.ModelAdmin):
    list_display = ['score', 'message']
    ordering = ['score']

admin.site.register(GameResultMessage, GameResultMessageAdmin)

class GameResultHistoryAdmin(admin.ModelAdmin):
    list_display = ['player', 'score', 'datetime']
    ordering = ['datetime']

admin.site.register(GameResultHistory, GameResultHistoryAdmin)

class ModifiedPreferencesAdmin(PreferencesAdmin):
    exclude = ('sites', 'streamlabs_access_token')

admin.site.register(ConfigSetting, ModifiedPreferencesAdmin)

class PremadePollAdmin(admin.ModelAdmin):
    list_display = ['title', 'multi', 'options']
    list_editable = ['title', 'multi', 'options']
    list_display_links = None
    ordering = ['title']
    search_fields = ['title']

admin.site.register(PremadePoll, PremadePollAdmin)
