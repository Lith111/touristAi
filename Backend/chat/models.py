from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class ChatSession(models.Model):
    SESSION_STATUS = (
        ('active', 'نشطة'),
        ('plan_generated', 'تم توليد الخطة'),
        ('price_quoted', 'تم التسعير'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغاة'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions', verbose_name=_('المستخدم'))
    session_id = models.CharField(_('معرف الجلسة'), max_length=100, unique=True)
    initial_requirements = models.JSONField(_('المتطلبات الأولية'), default=dict)
    conversation_history = models.JSONField(_('سجل المحادثة'), default=list)
    extracted_preferences = models.JSONField(_('التفضيلات المستخلصة'), default=dict)
    generated_plan = models.JSONField(_('الخطة المولدة'), default=dict)
    budget_range = models.JSONField(_('نطاق الميزانية'), default=dict)
    duration_days = models.PositiveIntegerField(_('عدد الأيام'), blank=True, null=True)
    status = models.CharField(_('حالة الجلسة'), max_length=20, choices=SESSION_STATUS, default='active')
    estimated_price = models.DecimalField(_('السعر التقريبي'), max_digits=10, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(_('السعر النهائي'), max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)
    expires_at = models.DateTimeField(_('تاريخ الانتهاء'))

    class Meta:
        db_table = 'chat_sessions'
        verbose_name = _('جلسة محادثة')
        verbose_name_plural = _('جلسات المحادثة')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.session_id}"

    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

class TravelPreference(models.Model):
    PREFERENCE_TYPES = (
        ('accommodation', 'الإقامة'),
        ('transportation', 'المواصلات'),
        ('food', 'الطعام'),
        ('activities', 'الأنشطة'),
        ('budget', 'الميزانية'),
        ('pace', 'سرعة الرحلة'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='travel_preferences', verbose_name=_('المستخدم'))
    preference_type = models.CharField(_('نوع التفضيل'), max_length=20, choices=PREFERENCE_TYPES)
    preference_key = models.CharField(_('مفتاح التفضيل'), max_length=100)
    preference_value = models.JSONField(_('قيمة التفضيل'), default=dict)
    weight = models.FloatField(_('الأهمية'), default=1.0)  # من 0 إلى 1
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'travel_preferences'
        verbose_name = _('تفضيل سفر')
        verbose_name_plural = _('تفضيلات السفر')
        unique_together = ['user', 'preference_type', 'preference_key']
        indexes = [
            models.Index(fields=['user', 'preference_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.preference_type}"

class AIRecommendationLog(models.Model):
    RECOMMENDATION_TYPES = (
        ('destination', 'وجهة'),
        ('package', 'باقة'),
        ('service', 'خدمة'),
        ('custom_plan', 'خطة مخصصة'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('المستخدم'))
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='recommendations', verbose_name=_('جلسة المحادثة'))
    recommendation_type = models.CharField(_('نوع التوصية'), max_length=20, choices=RECOMMENDATION_TYPES)
    input_parameters = models.JSONField(_('معاملات الإدخال'), default=dict)
    output_recommendations = models.JSONField(_('التوصيات المخرجة'), default=list)
    confidence_score = models.FloatField(_('درجة الثقة'), default=0.0)
    user_feedback = models.CharField(_('تقييم المستخدم'), max_length=10, blank=True, null=True)  # like/dislike
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        db_table = 'ai_recommendation_logs'
        verbose_name = _('سجل توصيات الذكاء الاصطناعي')
        verbose_name_plural = _('سجلات توصيات الذكاء الاصطناعي')
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.recommendation_type} - {self.confidence_score}"