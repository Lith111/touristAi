from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from bookings.models import Booking

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'قيد الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('completed', 'مكتمل'),
        ('failed', 'فاشل'),
        ('refunded', 'تم الاسترداد'),
        ('cancelled', 'ملغى'),
    )
    
    PAYMENT_METHODS = (
        ('credit_card', 'بطاقة ائتمان'),
        ('debit_card', 'بطاقة خصم'),
        ('bank_transfer', 'تحويل بنكي'),
        ('digital_wallet', 'محفظة إلكترونية'),
    )
    
    CURRENCIES = (
        ('SYP', 'ليرة سورية'),
        ('USD', 'دولار أمريكي'),
        ('EUR', 'يورو'),
    )
    
    payment_number = models.CharField(_('رقم الدفع'), max_length=20, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', verbose_name=_('الحجز'))
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('العملة'), max_length=3, choices=CURRENCIES, default='SYP')
    payment_method = models.CharField(_('طريقة الدفع'), max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(_('حالة الدفع'), max_length=15, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(_('معرف المعاملة'), max_length=100, blank=True, null=True)
    payment_gateway = models.CharField(_('بوابة الدفع'), max_length=50, blank=True, null=True)
    payment_gateway_response = models.JSONField(_('رد بوابة الدفع'), blank=True, null=True)
    payment_date = models.DateTimeField(_('تاريخ الدفع'), blank=True, null=True)
    refund_amount = models.DecimalField(_('مبلغ الاسترداد'), max_digits=10, decimal_places=2, default=0)
    refund_date = models.DateTimeField(_('تاريخ الاسترداد'), blank=True, null=True)
    refund_reason = models.TextField(_('سبب الاسترداد'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.payment_number} - {self.booking.booking_number}"

    def save(self, *args, **kwargs):
        if not self.payment_number:
            import random
            import string
            self.payment_number = 'PAY' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def can_refund(self):
        return self.status == 'completed' and self.refund_amount == 0

class PaymentGateway(models.Model):
    """نموذج لإعدادات بوابات الدفع"""
    name = models.CharField(_('الاسم'), max_length=100)
    gateway_type = models.CharField(_('النوع'), max_length=50)
    is_active = models.BooleanField(_('نشط'), default=True)
    credentials = models.JSONField(_('بيانات الاعتماد'), default=dict)
    test_mode = models.BooleanField(_('وضع الاختبار'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'payment_gateways'
        verbose_name = _('بوابة دفع')
        verbose_name_plural = _('بوابات الدفع')

    def __str__(self):
        return self.name