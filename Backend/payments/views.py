from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Payment, PaymentGateway
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentMethodSerializer,
    RefundRequestSerializer, PaymentGatewaySerializer
)
from rest_framework import serializers
from .services import PaymentProcessor
from bookings.models import Booking

class PaymentListView(generics.ListAPIView):
    """قائمة الدفعات للمستخدم"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user).select_related(
            'booking', 'booking__package', 'booking__custom_trip'
        ).order_by('-created_at')

class PaymentDetailView(generics.RetrieveAPIView):
    """تفاصيل دفعة معينة"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'payment_number'

    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user)

class PaymentCreateView(generics.CreateAPIView):
    """إنشاء دفعة جديدة"""
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        with transaction.atomic():
            payment = serializer.save()
            
            # معالجة الدفعة
            success = PaymentProcessor.process_payment(payment)
            
            if not success:
                raise serializers.ValidationError("فشل في معالجة الدفعة")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request, booking_number):
    """بدء عملية دفع لحجز معين"""
    try:
        booking = Booking.objects.get(booking_number=booking_number, user=request.user)
        
        # التحقق من أن الحجز في حالة يمكن الدفع لها
        if booking.status not in ['confirmed', 'pending']:
            return Response(
                {'error': 'لا يمكن الدفع لهذا الحجز في حالته الحالية'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # التحقق من عدم وجود دفعة سابقة ناجحة لنفس الحجز
        existing_payment = Payment.objects.filter(
            booking=booking, 
            status='completed'
        ).first()
        
        if existing_payment:
            return Response(
                {'error': 'تم دفع هذا الحجز مسبقاً'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # إنشاء دفعة جديدة
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            payment_method=request.data.get('payment_method', 'credit_card'),
            currency=request.data.get('currency', 'SYP')
        )

        # معالجة الدفعة
        success = PaymentProcessor.process_payment(payment)
        
        if success:
            serializer = PaymentSerializer(payment)
            return Response({
                'message': 'تمت عملية الدفع بنجاح',
                'payment': serializer.data
            })
        else:
            return Response({
                'error': 'فشلت عملية الدفع',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_400_BAD_REQUEST)

    except Booking.DoesNotExist:
        return Response(
            {'error': 'الحجز غير موجود'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_refund(request):
    """طلب استرداد أموال"""
    serializer = RefundRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            payment = Payment.objects.get(
                id=serializer.validated_data['payment_id'],
                booking__user=request.user
            )
            
            success, message = PaymentProcessor.process_refund(
                payment,
                serializer.validated_data['refund_amount'],
                serializer.validated_data['reason']
            )
            
            if success:
                return Response({'message': message})
            else:
                return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
                
        except Payment.DoesNotExist:
            return Response(
                {'error': 'الدفعة غير موجودة'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def payment_methods(request):
    """الحصول على طرق الدفع المتاحة"""
    methods = [
        {'value': method[0], 'label': method[1]} 
        for method in Payment.PAYMENT_METHODS
    ]
    return Response(methods)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def currencies(request):
    """الحصول على العملات المتاحة"""
    currencies_list = [
        {'value': currency[0], 'label': currency[1]} 
        for currency in Payment.CURRENCIES
    ]
    return Response(currencies_list)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def payment_webhook(request):
    """ويب هوك لاستقبال تحديثات الدفع من بوابة الدفع"""
    # هذه الوظيفة ستستخدم من قبل بوابة الدفع لإعلامنا بتحديثات الحالة
    data = request.data
    payment_number = data.get('payment_number')
    status = data.get('status')
    transaction_id = data.get('transaction_id')

    try:
        payment = Payment.objects.get(payment_number=payment_number)
        payment.status = status
        payment.transaction_id = transaction_id
        payment.payment_gateway_response = data
        
        if status == 'completed':
            payment.payment_date = timezone.now()
            # تحديث حالة الحجز
            booking = payment.booking
            booking.status = 'paid'
            booking.save()
        
        payment.save()

        return Response({'message': 'تم تحديث حالة الدفع'})

    except Payment.DoesNotExist:
        return Response(
            {'error': 'الدفعة غير موجودة'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class PaymentGatewayListView(generics.ListAPIView):
    """قائمة بوابات الدفع المتاحة"""
    queryset = PaymentGateway.objects.filter(is_active=True)
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.AllowAny]