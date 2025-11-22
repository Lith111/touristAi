from django.contrib import admin
from .models import CustomTrip, CustomTripDestination, CustomTripService, Booking

class CustomTripDestinationInline(admin.TabularInline):
    model = CustomTripDestination
    extra = 1

class CustomTripServiceInline(admin.TabularInline):
    model = CustomTripService
    extra = 1

@admin.register(CustomTrip)
class CustomTripAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'duration_days', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'user__username')
    list_editable = ('status', 'total_price')
    inlines = [CustomTripDestinationInline, CustomTripServiceInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'user', 'booking_type', 'status', 'total_price', 'start_date', 'booking_date')
    list_filter = ('booking_type', 'status', 'start_date')
    search_fields = ('booking_number', 'user__username')
    list_editable = ('status',)
    readonly_fields = ('booking_number', 'booking_date')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'package', 'custom_trip')