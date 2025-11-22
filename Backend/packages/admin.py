from django.contrib import admin
from .models import Destination, Service, Package, PackageDestination, PackageService

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'governorate', 'popularity_score', 'is_active', 'created_at')
    list_filter = ('type', 'governorate', 'is_active')
    search_fields = ('name', 'governorate', 'description')
    list_editable = ('is_active', 'popularity_score')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'level', 'destination', 'price_per_unit', 'is_active', 'created_at')
    list_filter = ('type', 'level', 'destination', 'is_active')
    search_fields = ('name', 'description', 'address')
    list_editable = ('is_active', 'price_per_unit')

class PackageDestinationInline(admin.TabularInline):
    model = PackageDestination
    extra = 1

class PackageServiceInline(admin.TabularInline):
    model = PackageService
    extra = 1

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'duration_days', 'base_price', 'discount_price', 'is_featured', 'is_active', 'created_at')
    list_filter = ('type', 'is_featured', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('is_featured', 'is_active', 'base_price', 'discount_price')
    inlines = [PackageDestinationInline, PackageServiceInline]