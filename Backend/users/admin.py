from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
import csv
from .models import User

class CustomUserAdmin(UserAdmin):
    """تخصيص واجهة إدارة المستخدمين"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'is_staff', 'date_joined', 'user_bookings_count', 'user_custom_trips_count')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('المعلومات الشخصية'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'date_of_birth')
        }),
        (_('معلومات السفر'), {
            'fields': ('nationality', 'passport_number', 'preferences')
        }),
        (_('الصلاحيات'), {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('تواريخ مهمة'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_verified', 'is_active', 'is_staff'),
        }),
    )
    
    # إصلاح: جعل أسماء الإجراءات فريدة
    actions = ['verify_selected_users', 'unverify_selected_users', 'activate_selected_users', 
               'deactivate_selected_users', 'promote_to_admin', 'demote_to_user', 
               'export_user_data', 'send_bulk_email', 'analyze_user_behavior']
    
    def verify_selected_users(self, request, queryset):
        """تصديق المستخدمين المحددين"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'تم تصديق {updated} مستخدم')
    verify_selected_users.short_description = "تصديق المستخدمين المحددين"
    
    def unverify_selected_users(self, request, queryset):
        """إلغاء تصديق المستخدمين المحددين"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'تم إلغاء تصديق {updated} مستخدم')
    unverify_selected_users.short_description = "إلغاء تصديق المستخدمين المحددين"
    
    def activate_selected_users(self, request, queryset):
        """تفعيل المستخدمين المحددين"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} مستخدم')
    activate_selected_users.short_description = "تفعيل المستخدمين المحددين"
    
    def deactivate_selected_users(self, request, queryset):
        """تعطيل المستخدمين المحددين"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} مستخدم')
    deactivate_selected_users.short_description = "تعطيل المستخدمين المحددين"
    
    def promote_to_admin(self, request, queryset):
        """تحويل المستخدمين إلى مدراء"""
        updated = queryset.update(role='admin', is_staff=True)
        self.message_user(request, f'تم تحويل {updated} مستخدم إلى مدراء')
    promote_to_admin.short_description = "ترقية المستخدمين إلى مدراء"
    
    def demote_to_user(self, request, queryset):
        """إزالة صلاحيات المدير من المستخدمين"""
        updated = queryset.update(role='user', is_staff=False)
        self.message_user(request, f'تم إزالة صلاحيات المدير من {updated} مستخدم')
    demote_to_user.short_description = "خفض رتبة المستخدمين إلى مستخدمين عاديين"
    
    def export_user_data(self, request, queryset):
        """تصدير بيانات المستخدمين المحددين"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        
        # كتابة BOM لضمان دعم اللغة العربية في Excel
        response.write('\ufeff')
        
        writer = csv.writer(response)
        writer.writerow([
            'اسم المستخدم', 'البريد الإلكتروني', 'الاسم الكامل', 'الهاتف', 'الدور', 
            'مؤكد', 'نشط', 'عدد الحجوزات', 'عدد الرحلات', 'تاريخ الانضمام'
        ])
        
        for user in queryset:
            writer.writerow([
                user.username,
                user.email,
                user.full_name,
                user.phone or '',
                user.get_role_display(),
                'نعم' if user.is_verified else 'لا',
                'نعم' if user.is_active else 'لا',
                user.bookings_count,
                user.custom_trips_count,
                user.date_joined.strftime('%Y-%m-%d')
            ])
        
        return response
    export_user_data.short_description = "تصدير بيانات المستخدمين المحددين (CSV)"
    
    def send_bulk_email(self, request, queryset):
        """إرسال بريد إلكتروني جماعي للمستخدمين المحددين"""
        emails = [user.email for user in queryset if user.email]
        self.message_user(
            request, 
            f'تم إعداد إرسال بريد إلكتروني إلى {len(emails)} مستخدم'
        )
    send_bulk_email.short_description = "إرسال بريد إلكتروني للمستخدمين المحددين"
    
    def analyze_user_behavior(self, request, queryset):
        """تحليل سلوك المستخدمين المحددين"""
        from django.db.models import Count, Avg
        from bookings.models import Booking
        
        analysis_results = []
        
        for user in queryset:
            user_data = {
                'user': user.username,
                'total_bookings': user.bookings_count,
                'custom_trips': user.custom_trips_count,
                'chat_sessions': user.chat_sessions_count,
                'total_spent': user.total_spent,
                'last_activity': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'لم يسجل دخول'
            }
            
            analysis_results.append(user_data)
        
        # عرض النتائج في رسالة
        message = "تحليل سلوك المستخدمين:\n\n"
        for result in analysis_results:
            message += f"المستخدم: {result['user']}\n"
            message += f"عدد الحجوزات: {result['total_bookings']}\n"
            message += f"عدد الرحلات المخصصة: {result['custom_trips']}\n"
            message += f"إجمالي الإنفاق: {result['total_spent']} ل.س\n"
            message += f"آخر نشاط: {result['last_activity']}\n"
            message += "---\n"
        
        self.message_user(request, message)
    analyze_user_behavior.short_description = "تحليل سلوك المستخدمين المحددين"
    
    def get_queryset(self, request):
        """تخصيص الاستعلام للحصول على أداء أفضل"""
        return super().get_queryset(request).select_related().prefetch_related('groups', 'user_permissions')
    
    def user_bookings_count(self, obj):
        """عدد حجوزات المستخدم"""
        return obj.bookings.count()
    user_bookings_count.short_description = 'عدد الحجوزات'
    
    def user_custom_trips_count(self, obj):
        """عدد الرحلات المخصصة للمستخدم"""
        return obj.custom_trips.count()
    user_custom_trips_count.short_description = 'عدد الرحلات المخصصة'

# تسجيل النموذج مع الواجهة المخصصة
admin.site.register(User, CustomUserAdmin)