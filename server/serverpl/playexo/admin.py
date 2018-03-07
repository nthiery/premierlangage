from django.contrib import admin

from playexo.models import Activity, Answer

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display=('__str__', 'strategy', 'pltp')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display=('user', 'pl', 'seed', 'date')
