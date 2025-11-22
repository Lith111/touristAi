from django.contrib import admin
from .models import ChatSession, TravelPreference, AIRecommendationLog

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'status', 'duration_days', 'estimated_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('session_id', 'user__username')
    list_editable = ('status',)
    readonly_fields = ('session_id', 'id')

@admin.register(TravelPreference)
class TravelPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'preference_type', 'preference_key', 'weight', 'created_at')
    list_filter = ('preference_type',)
    search_fields = ('user__username', 'preference_key')

@admin.register(AIRecommendationLog)
class AIRecommendationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'confidence_score', 'user_feedback', 'created_at')
    list_filter = ('recommendation_type', 'user_feedback')
    search_fields = ('user__username',)