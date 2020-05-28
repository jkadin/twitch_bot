from django.contrib import admin

from .models import Player, GameResult, ConfigurationSetting


admin.site.site_header = ConfigurationSetting.objects.get(key='Game Title').value
admin.site.site_title = ConfigurationSetting.objects.get(key='Game Title').value


class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Player Info', {'fields': ['username', 'score']}),
]
    list_display = ('username', 'score')
    search_fields = ['username']

admin.site.register(Player, PlayerAdmin)

admin.site.register(GameResult)


class ConfigurationSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    list_editable = ['value']
    ordering = ['key']
    list_display_links = None

admin.site.register(ConfigurationSetting, ConfigurationSettingAdmin)
