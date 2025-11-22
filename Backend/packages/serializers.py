from rest_framework import serializers
from .models import Destination, Service, Package, PackageDestination, PackageService

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'

class PackageDestinationSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    destination_type = serializers.CharField(source='destination.type', read_only=True)
    
    class Meta:
        model = PackageDestination
        fields = '__all__'

class PackageServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_type = serializers.CharField(source='service.type', read_only=True)
    
    class Meta:
        model = PackageService
        fields = '__all__'

class PackageListSerializer(serializers.ModelSerializer):
    destinations = DestinationSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Package
        fields = [
            'id', 'title', 'type', 'short_description', 'duration_days',
            'base_price', 'discount_price', 'final_price', 'image_urls',
            'is_featured', 'destinations'
        ]

class PackageDetailSerializer(serializers.ModelSerializer):
    destinations = PackageDestinationSerializer(source='packagedestination_set', many=True, read_only=True)
    services = PackageServiceSerializer(source='packageservice_set', many=True, read_only=True)
    included_services_list = ServiceSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Package
        fields = '__all__'

class PackageSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    package_type = serializers.CharField(required=False)
    governorate = serializers.CharField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_duration = serializers.IntegerField(required=False)
    max_duration = serializers.IntegerField(required=False)
    is_featured = serializers.BooleanField(required=False)