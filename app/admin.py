from django.contrib import admin
from .views import AnalysisResult

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'wqi_score', 'clarity_score')
    list_filter = ('user', 'timestamp')
    search_fields = ('user__username',)
