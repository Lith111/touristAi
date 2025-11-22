from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from packages.models import Package

class CustomTrip(models.Model):
    TRIP_STATUS = (
        ('draft', 'مسودة'),
        ('quoted', 'مسعر'),
        ('confirmed', 'مؤكد'),
        ('booked', 'محجوز'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغى'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_trips', verbose_name=_('المستخدم'))
    title = models.CharField(_('عنوان الرحلة'), max_length=200)
    destinations = models.ManyToManyField('packages.Destination', through='CustomTripDestination', verbose_name=_('الوجهات'))
    services = models.ManyToManyField('packages.Service', through='CustomTripService', verbose_name=_('الخدمات'))
    duration_days = models.PositiveIntegerField(_('عدد الأيام'))
    total_price = models.DecimalField(_('السعر الإجمالي'), max_digits=10, decimal_places=2, default=0)
    daily_plan = models.JSONField(_('الخطة اليومية'), default=dict)
    included_services = models.JSONField(_('الخدمات المشمولة'), default=list)
    special_requests = models.TextField(_('طلبات خاصة'), blank=True, null=True)
    status = models.CharField(_('الحالة'), max_length=15, choices=TRIP_STATUS, default='draft')
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'custom_trips'
        verbose_name = _('رحلة مخصصة')
        verbose_name_plural = _('الرحلات المخصصة')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class CustomTripDestination(models.Model):
    custom_trip = models.ForeignKey(CustomTrip, on_delete=models.CASCADE, verbose_name=_('الرحلة المخصصة'))
    destination = models.ForeignKey('packages.Destination', on_delete=models.CASCADE, verbose_name=_('الوجهة'))
    visit_order = models.PositiveIntegerField(_('ترتيب الزيارة'))
    duration_hours = models.PositiveIntegerField(_('المدة بالساعات'))
    visit_date = models.DateField(_('تاريخ الزيارة'), blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        db_table = 'custom_trip_destinations'
        verbose_name = _('وجهة الرحلة المخصصة')
        verbose_name_plural = _('وجهات الرحلات المخصصة')
        unique_together = ['custom_trip', 'destination']
        ordering = ['visit_order']

class CustomTripService(models.Model):
    TIME_SLOTS = (
        ('morning', 'صباح'),
        ('afternoon', 'بعد الظهر'),
        ('evening', 'مساء'),
    )
    
    custom_trip = models.ForeignKey(CustomTrip, on_delete=models.CASCADE, verbose_name=_('الرحلة المخصصة'))
    service = models.ForeignKey('packages.Service', on_delete=models.CASCADE, verbose_name=_('الخدمة'))
    day_number = models.PositiveIntegerField(_('رقم اليوم'))
    time_slot = models.CharField(_('الفترة'), max_length=10, choices=TIME_SLOTS)
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    date = models.DateField(_('التاريخ'), blank=True, null=True)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        db_table = 'custom_trip_services'
        verbose_name = _('خدمة الرحلة المخصصة')
        verbose_name_plural = _('خدمات الرحلات المخصصة')
        ordering = ['day_number', 'time_slot']

class Booking(models.Model):
    BOOKING_TYPES = (
        ('package', 'باقة جاهزة'),
        ('custom', 'رحلة مخصصة'),
    )
    
    BOOKING_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'مؤكد'),
        ('paid', 'مدفوع'),
        ('active', 'نشط'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغى'),
        ('refunded', 'تم الاسترداد'),
    )
    
    booking_number = models.CharField(_('رقم الحجز'), max_length=20, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', verbose_name=_('المستخدم'))
    booking_type = models.CharField(_('نوع الحجز'), max_length=10, choices=BOOKING_TYPES)
    package = models.ForeignKey('packages.Package', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('الباقة'))
    custom_trip = models.ForeignKey(CustomTrip, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('الرحلة المخصصة'))
    status = models.CharField(_('حالة الحجز'), max_length=15, choices=BOOKING_STATUS, default='pending')
    total_price = models.DecimalField(_('السعر الإجمالي'), max_digits=10, decimal_places=2)
    number_of_travelers = models.PositiveIntegerField(_('عدد المسافرين'), default=1)
    traveler_details = models.JSONField(_('تفاصيل المسافرين'), default=list)
    special_requests = models.TextField(_('طلبات خاصة'), blank=True, null=True)
    start_date = models.DateField(_('تاريخ البدء'))
    end_date = models.DateField(_('تاريخ الانتهاء'))
    booking_date = models.DateTimeField(_('تاريخ الحجز'), auto_now_add=True)
    confirmation_date = models.DateTimeField(_('تاريخ التأكيد'), blank=True, null=True)
    cancellation_date = models.DateTimeField(_('تاريخ الإلغاء'), blank=True, null=True)
    cancellation_reason = models.TextField(_('سبب الإلغاء'), blank=True, null=True)
    @property
    def has_successful_payment(self):
        """التحقق من وجود دفعة ناجحة للحجز"""
        return self.payments.filter(status='completed').exists()
    
    @property
    def last_payment(self):
        """آخر دفعة للحجز"""
        return self.payments.order_by('-created_at').first()
    class Meta:
        db_table = 'bookings'
        verbose_name = _('حجز')
        verbose_name_plural = _('الحجوزات')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_number']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.booking_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            # إنشاء رقم حجز فريد
            import random
            import string
            self.booking_number = 'BK' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)