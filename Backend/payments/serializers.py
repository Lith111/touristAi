from rest_framework import serializers
from .models import Payment, PaymentGateway

class PaymentSerializer(serializers.ModelSerializer):
    booking_number = serializers.CharField(source='booking.booking_number', read_only=True)
    user_name = serializers.CharField(source='booking.user.get_full_name', read_only=True)
    package_title = serializers.CharField(source='booking.package.title', read_only=True, allow_null=True)
    custom_trip_title = serializers.CharField(source='booking.custom_trip.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('payment_number', 'transaction_id', 'payment_gateway_response', 
                           'payment_date', 'refund_date', 'created_at', 'updated_at')

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'currency', 'payment_method']
    
    def validate(self, data):
        booking = data['booking']
        
        # التحقق من أن الحجز للمستخدم الحالي
        if booking.user != self.context['request'].user:
            raise serializers.ValidationError("هذا الحجز لا ينتمي إليك.")
        
        # التحقق من أن الحجز في حالة يمكن الدفع لها
        if booking.status not in ['confirmed', 'pending']:
            raise serializers.ValidationError("لا يمكن الدفع لهذا الحجز في حالته الحالية.")
        
        # التحقق من أن المبلغ مطابق للسعر الإجمالي
        if data['amount'] != booking.total_price:
            raise serializers.ValidationError("المبلغ غير مطابق للسعر الإجمالي للحجز.")
        
        return data

class PaymentMethodSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS)
    currency = serializers.ChoiceField(choices=Payment.CURRENCIES, default='SYP')

class RefundRequestSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=500)
    
    def validate_refund_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("مبلغ الاسترداد يجب أن يكون أكبر من الصفر.")
        return value

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'gateway_type', 'is_active', 'test_mode']