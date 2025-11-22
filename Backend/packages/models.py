from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Destination(models.Model):
    DESTINATION_TYPES = (
        ('city', 'مدينة'),
        ('historical', 'موقع تاريخي'),
        ('natural', 'موقع طبيعي'),
        ('coastal', 'ساحلي'),
    )
    
    name = models.CharField(_('الاسم'), max_length=100)
    type = models.CharField(_('النوع'), max_length=20, choices=DESTINATION_TYPES)
    description = models.TextField(_('الوصف'))
    governorate = models.CharField(_('المحافظة'), max_length=50)
    latitude = models.FloatField(_('خط العرض'))
    longitude = models.FloatField(_('خط الطول'))
    popularity_score = models.IntegerField(_('مستوى الشعبية'), default=0)
    best_season = models.CharField(_('أفضل موسم'), max_length=100)
    image_url = models.URLField(_('صورة'), blank=True, null=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        db_table = 'destinations'
        verbose_name = _('وجهة')
        verbose_name_plural = _('الوجهات')
        indexes = [
            models.Index(fields=['governorate', 'type']),
            models.Index(fields=['popularity_score']),
        ]

    def __str__(self):
        return self.name

class Service(models.Model):
    SERVICE_TYPES = (
        ('hotel', 'فندق'),
        ('transport', 'مواصلات'),
        ('restaurant', 'مطعم'),
        ('activity', 'نشاط ترفيهي'),
        ('guide', 'مرشد سياحي'),
    )
    
    SERVICE_LEVELS = (
        ('economy', 'اقتصادي'),
        ('standard', 'قياسي'),
        ('premium', 'متميز'),
        ('luxury', 'فاخر'),
    )
    
    name = models.CharField(_('الاسم'), max_length=200)
    type = models.CharField(_('النوع'), max_length=20, choices=SERVICE_TYPES)
    level = models.CharField(_('المستوى'), max_length=15, choices=SERVICE_LEVELS, default='standard')
    description = models.TextField(_('الوصف'))
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='services', verbose_name=_('الوجهة'))
    address = models.TextField(_('العنوان'))
    contact_phone = models.CharField(_('رقم الهاتف'), max_length=15, blank=True, null=True)
    contact_email = models.EmailField(_('البريد الإلكتروني'), blank=True, null=True)
    price_per_unit = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    unit_description = models.CharField(_('وصف الوحدة'), max_length=100)
    capacity = models.IntegerField(_('السعة'), blank=True, null=True)
    features = models.JSONField(_('المميزات'), default=list)
    rating = models.FloatField(_('التقييم'), default=0.0)
    image_urls = models.JSONField(_('الصور'), default=list)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'services'
        verbose_name = _('خدمة')
        verbose_name_plural = _('الخدمات')
        indexes = [
            models.Index(fields=['type', 'level']),
            models.Index(fields=['destination', 'type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Package(models.Model):
    PACKAGE_TYPES = (
        ('family', 'عائلية'),
        ('adventure', 'مغامرة'),
        ('cultural', 'ثقافية'),
        ('honeymoon', 'شهر عسل'),
        ('religious', 'دينية'),
    )
    
    title = models.CharField(_('العنوان'), max_length=200)
    type = models.CharField(_('النوع'), max_length=20, choices=PACKAGE_TYPES)
    description = models.TextField(_('الوصف'))
    short_description = models.CharField(_('وصف مختصر'), max_length=300)
    duration_days = models.PositiveIntegerField(_('عدد الأيام'))
    base_price = models.DecimalField(_('السعر الأساسي'), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(_('سعر الخصم'), max_digits=10, decimal_places=2, blank=True, null=True)
    destinations = models.ManyToManyField(Destination, through='PackageDestination', verbose_name=_('الوجهات'))
    services = models.ManyToManyField(Service, through='PackageService', verbose_name=_('الخدمات'))
    included_services = models.JSONField(_('الخدمات المشمولة'), default=list)
    excluded_services = models.JSONField(_('الخدمات غير المشمولة'), default=list)
    daily_schedule = models.JSONField(_('الجدول اليومي'))
    terms_conditions = models.TextField(_('الشروط والأحكام'))
    cancellation_policy = models.TextField(_('سياسة الإلغاء'))
    image_urls = models.JSONField(_('الصور'), default=list)
    popularity_count = models.IntegerField(_('عدد المشاهدات'), default=0)
    is_featured = models.BooleanField(_('مميز'), default=False)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        db_table = 'packages'
        verbose_name = _('باقة')
        verbose_name_plural = _('الباقات')
        indexes = [
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['base_price']),
        ]

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.base_price

class PackageDestination(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, verbose_name=_('الباقة'))
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name=_('الوجهة'))
    visit_order = models.PositiveIntegerField(_('ترتيب الزيارة'))
    duration_hours = models.PositiveIntegerField(_('المدة بالساعات'))
    description = models.TextField(_('الوصف'), blank=True, null=True)

    class Meta:
        db_table = 'package_destinations'
        verbose_name = _('وجهة الباقة')
        verbose_name_plural = _('وجهات الباقات')
        unique_together = ['package', 'destination']
        ordering = ['visit_order']

    def __str__(self):
        return f"{self.package.title} - {self.destination.name}"

class PackageService(models.Model):
    TIME_SLOTS = (
        ('morning', 'صباح'),
        ('afternoon', 'بعد الظهر'),
        ('evening', 'مساء'),
    )
    
    package = models.ForeignKey(Package, on_delete=models.CASCADE, verbose_name=_('الباقة'))
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name=_('الخدمة'))
    day_number = models.PositiveIntegerField(_('رقم اليوم'))
    time_slot = models.CharField(_('الفترة'), max_length=10, choices=TIME_SLOTS)
    quantity = models.PositiveIntegerField(_('الكمية'), default=1)
    notes = models.TextField(_('ملاحظات'), blank=True, null=True)

    class Meta:
        db_table = 'package_services'
        verbose_name = _('خدمة الباقة')
        verbose_name_plural = _('خدمات الباقات')
        ordering = ['day_number', 'time_slot']

    def __str__(self):
        return f"{self.package.title} - {self.service.name} - اليوم {self.day_number}"