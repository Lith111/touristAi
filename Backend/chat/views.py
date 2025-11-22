from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import ChatSession, TravelPreference, AIRecommendationLog
from .serializers import (
    ChatMessageSerializer, ChatSessionSerializer, 
    TravelPreferenceSerializer, TravelRequirementsSerializer
)
from .ai_service import AITravelAssistant

class ChatSessionListView(generics.ListCreateAPIView):
    """قائمة جلسات المحادثة للمستخدم"""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, expires_at=timezone.now() + timedelta(hours=24))

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chat_message(request):
    """إرسال رسالة إلى المساعد الافتراضي"""
    serializer = ChatMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        
        # الحصول على الجلسة أو إنشاء جديدة
        if session_id:
            try:
                chat_session = ChatSession.objects.get(
                    session_id=session_id, 
                    user=request.user
                )
            except ChatSession.DoesNotExist:
                return Response(
                    {'error': 'الجلسة غير موجودة'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            chat_session = ChatSession.objects.create(
                user=request.user,
                expires_at=timezone.now() + timedelta(hours=24)
            )
        
        # تحديث سجل المحادثة
        conversation_history = chat_session.conversation_history
        conversation_history.append({
            'role': 'user',
            'message': message,
            'timestamp': timezone.now().isoformat()
        })
        
        # استخراج المتطلبات من المحادثة
        requirements = chat_session.initial_requirements
        request._extract_requirements_from_message(message, requirements)
        
        # الحصول على رد الذكاء الاصطناعي
        ai_assistant = AITravelAssistant()
        ai_response = ai_assistant.generate_response(conversation_history, requirements)
        
        # إضافة رد الذكاء الاصطناعي إلى سجل المحادثة
        conversation_history.append({
            'role': 'assistant',
            'message': ai_response['message'],
            'action': ai_response['action'],
            'timestamp': timezone.now().isoformat()
        })
        
        # حفظ التحديثات
        chat_session.conversation_history = conversation_history
        chat_session.initial_requirements = requirements
        chat_session.save()
        
        return Response({
            'session_id': chat_session.session_id,
            'response': ai_response,
            'conversation_history': conversation_history
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_travel_plan(request):
    """توليد خطة سفر مكتملة"""
    serializer = TravelRequirementsSerializer(data=request.data)
    
    if serializer.is_valid():
        requirements = serializer.validated_data
        
        # توليد الخطة باستخدام الذكاء الاصطناعي
        ai_assistant = AITravelAssistant()
        travel_plan = ai_assistant.generate_travel_plan(requirements)
        
        # إنشاء سجل للتوصية
        recommendation_log = AIRecommendationLog.objects.create(
            user=request.user,
            recommendation_type='custom_plan',
            input_parameters=requirements,
            output_recommendations=travel_plan,
            confidence_score=0.85  # محاكاة لدرجة الثقة
        )
        
        return Response({
            'plan': travel_plan,
            'recommendation_id': recommendation_log.id
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def _extract_requirements_from_message(self, message, requirements):
    """استخراج المتطلبات من رسالة المستخدم (محاكاة)"""
    # في الإصدار الحقيقي، سيستخدم هذا معالجة اللغة الطبيعية
    message_lower = message.lower()
    
    if 'ميزانية' in message_lower or 'سعر' in message_lower:
        # محاكاة استخراج الميزانية
        requirements['budget'] = {'total': 1000}
    if 'أيام' in message_lower or 'مدة' in message_lower:
        # محاكاة استخراج المدة
        requirements['duration_days'] = 3

class TravelPreferenceView(generics.ListCreateAPIView):
    """إدارة تفضيلات السفر"""
    serializer_class = TravelPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TravelPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)