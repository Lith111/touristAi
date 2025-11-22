from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.ChatSessionListView.as_view(), name='chat-sessions'),
    path('message/', views.chat_message, name='chat-message'),
    path('generate-plan/', views.generate_travel_plan, name='generate-plan'),
    path('preferences/', views.TravelPreferenceView.as_view(), name='travel-preferences'),
]