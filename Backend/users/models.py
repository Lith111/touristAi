from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    USER_ROLES = (
        ('user', 'مستخدم عادي'),
        ('admin', 'مدير النظام'),
    )
    
    role = models.CharField(_('الدور'), max_length=10, choices=USER_ROLES, default='user')
    phone = models.CharField(_('رقم الهاتف'), max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(_('تاريخ الميلاد'), blank=True, null=True)
    nationality = models.CharField(_('الجنسية'), max_length=50, blank=True, null=True)
    passport_number = models.CharField(_('رقم الجواز'), max_length=20, blank=True, null=True)
    preferences = models.JSONField(_('التفضيلات'), default=dict, blank=True)
    is_verified = models.BooleanField(_('مؤكد'), default=False)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_verified']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def bookings_count(self):
        """عدد حجوزات المستخدم"""
        return self.bookings.count()

    @property
    def custom_trips_count(self):
        """عدد الرحلات المخصصة للمستخدم"""
        return self.custom_trips.count()

    @property
    def chat_sessions_count(self):
        """عدد جلسات المحادثة للمستخدم"""
        return self.chat_sessions.count()

    @property
    def total_spent(self):
        """إجمالي ما أنفقه المستخدم"""
        from django.db.models import Sum
        return self.bookings.aggregate(
            total=Sum('total_price')
        )['total'] or 0

    @property
    def is_recently_joined(self):
        """هل انضم المستخدم مؤخراً؟ (خلال آخر 7 أيام)"""
        return self.date_joined >= timezone.now() - timedelta(days=7)

    @property
    def is_active_recently(self):
        """هل كان المستخدم نشطاً مؤخراً؟ (خلال آخر 30 يوم)"""
        if not self.last_login:
            return False
        return self.last_login >= timezone.now() - timedelta(days=30)

    def get_travel_preferences(self):
        """الحصول على تفضيلات السفر للمستخدم"""
        from chat.models import TravelPreference
        return TravelPreference.objects.filter(user=self)

    def get_booking_history(self):
        """سجل حجوزات المستخدم"""
        return self.bookings.select_related('package', 'custom_trip').order_by('-booking_date')

    def get_chat_history(self):
        """سجل محادثات المستخدم"""
        return self.chat_sessions.order_by('-created_at')

    def verify_user(self):
        """تصديق المستخدم"""
        self.is_verified = True
        self.save(update_fields=['is_verified', 'updated_at'])

    def deactivate_user(self):
        """تعطيل المستخدم"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def activate_user(self):
        """تفعيل المستخدم"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def promote_to_admin(self):
        """ترقية المستخدم إلى مدير"""
        self.role = 'admin'
        self.is_staff = True
        self.save(update_fields=['role', 'is_staff', 'updated_at'])

    def demote_to_user(self):
        """خفض رتبة المدير إلى مستخدم عادي"""
        self.role = 'user'
        self.is_staff = False
        self.save(update_fields=['role', 'is_staff', 'updated_at'])