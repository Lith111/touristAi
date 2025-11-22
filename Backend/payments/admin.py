from django.contrib import admin
from .models import Payment, PaymentGateway

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'booking', 'amount', 'currency', 'payment_method', 'status', 'payment_date', 'created_at')
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('payment_number', 'booking__booking_number', 'transaction_id')
    list_editable = ('status',)
    readonly_fields = ('payment_number', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'booking__user')

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'gateway_type', 'is_active', 'test_mode', 'created_at')
    list_filter = ('is_active', 'test_mode', 'gateway_type')
    list_editable = ('is_active', 'test_mode')