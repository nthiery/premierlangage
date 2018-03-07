from django.contrib import admin

from gitload.models import PLTP, PL, Repository, Strategy


@admin.register(PLTP)
class PltpAdmin(admin.ModelAdmin):
    list_display=('name', 'json', 'sha1')

@admin.register(PL)
class PlAdmin(admin.ModelAdmin):
    list_display=('name', 'sha1','json')
    
@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display=('name', 'json')
    
@admin.register(Repository)
class RepoAdmin(admin.ModelAdmin):
    list_display=('name', 'owner', 'url', 'version')
