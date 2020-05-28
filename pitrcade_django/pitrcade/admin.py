from django.contrib import admin

from .models import Player, GameResult, ConfigurationSetting


admin.site.site_header = ConfigurationSetting.objects.get(key='Game Title').value
admin.site.site_title = ConfigurationSetting.objects.get(key='Game Title').value


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Player Info', {'fields': ['username', 'score', 'num_quarters']}),
]
    list_display = ('username', 'score', 'num_quarters')
    search_fields = ['username']

admin.site.register(Player, PlayerAdmin)


class GameResultAdmin(admin.ModelAdmin):
    list_display = ['min_score', 'message']
    ordering = ['min_score']

admin.site.register(GameResult, GameResultAdmin)


class ConfigurationSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    list_editable = ['value']
    ordering = ['key']
    list_display_links = None

admin.site.register(ConfigurationSetting, ConfigurationSettingAdmin)
