from rest_framework import serializers
from .models import Booking, CustomTrip, CustomTripDestination, CustomTripService
from packages.serializers import PackageListSerializer, DestinationSerializer, ServiceSerializer

class CustomTripDestinationSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    
    class Meta:
        model = CustomTripDestination
        fields = '__all__'

class CustomTripServiceSerializer(serializers.ModelSerializer):
    service_details = ServiceSerializer(source='service', read_only=True)
    
    class Meta:
        model = CustomTripService
        fields = '__all__'

class CustomTripSerializer(serializers.ModelSerializer):
    destinations = CustomTripDestinationSerializer(source='customtripdestination_set', many=True, read_only=True)
    services = CustomTripServiceSerializer(source='customtripservice_set', many=True, read_only=True)
    
    class Meta:
        model = CustomTrip
        fields = '__all__'
        read_only_fields = ('user', 'status', 'created_at', 'updated_at')

class BookingSerializer(serializers.ModelSerializer):
    package_details = PackageListSerializer(source='package', read_only=True)
    custom_trip_details = CustomTripSerializer(source='custom_trip', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('booking_number', 'user', 'booking_date', 'confirmation_date', 'cancellation_date')

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['booking_type', 'package', 'custom_trip', 'number_of_travelers', 
                 'traveler_details', 'special_requests', 'start_date', 'end_date']
    
    def validate(self, data):
        # التحقق من أن إما الباقة أو الرحلة المخصصة محددة
        if data.get('package') and data.get('custom_trip'):
            raise serializers.ValidationError("لا يمكن اختيار باقة ورحلة مخصصة معاً")
        
        if not data.get('package') and not data.get('custom_trip'):
            raise serializers.ValidationError("يجب اختيار إما باقة أو رحلة مخصصة")
        
        # التحقق من تاريخ البداية والنهاية
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
        
        return data

class TravelerDetailSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    passport_number = serializers.CharField()
    nationality = serializers.CharField()