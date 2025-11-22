from rest_framework import serializers
from .models import ChatSession, TravelPreference, AIRecommendationLog

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.CharField(required=False)

class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'session_id', 'status', 'duration_days', 'estimated_price', 'created_at']

class TravelPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelPreference
        fields = '__all__'

class AIRecommendationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendationLog
        fields = '__all__'

class TravelRequirementsSerializer(serializers.Serializer):
    duration_days = serializers.IntegerField(min_value=1, max_value=30)
    number_of_travelers = serializers.IntegerField(min_value=1, max_value=20)
    budget = serializers.DictField(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    preferences = serializers.DictField(required=False)
    interests = serializers.ListField(child=serializers.CharField(), required=False)
    constraints = serializers.ListField(child=serializers.CharField(), required=False)