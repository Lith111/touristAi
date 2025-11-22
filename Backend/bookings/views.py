from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Booking, CustomTrip
from .serializers import BookingSerializer, BookingCreateSerializer, CustomTripSerializer

class BookingListView(generics.ListAPIView):
    """قائمة حجوزات المستخدم"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_fields = ['status', 'booking_type']

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related(
            'package', 'custom_trip'
        ).order_by('-booking_date')

class BookingDetailView(generics.RetrieveAPIView):
    """تفاصيل حجز معين"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'booking_number'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingCreateView(generics.CreateAPIView):
    """إنشاء حجز جديد"""
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        with transaction.atomic():
            # حساب السعر الإجمالي
            total_price = 0
            booking_data = serializer.validated_data
            
            if booking_data['booking_type'] == 'package' and booking_data['package']:
                package = booking_data['package']
                total_price = package.final_price * booking_data['number_of_travelers']
            elif booking_data['booking_type'] == 'custom' and booking_data['custom_trip']:
                custom_trip = booking_data['custom_trip']
                total_price = custom_trip.total_price
            
            # حفظ الحجز
            booking = serializer.save(user=self.request.user, total_price=total_price)
            
            # إذا كانت رحلة مخصصة، تحديث حالتها
            if booking_data['booking_type'] == 'custom' and booking_data['custom_trip']:
                custom_trip = booking_data['custom_trip']
                custom_trip.status = 'booked'
                custom_trip.save()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking(request, booking_number):
    """إلغاء الحجز"""
    try:
        booking = Booking.objects.get(
            booking_number=booking_number, 
            user=request.user
        )
        
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'لا يمكن إلغاء هذا الحجز في حالته الحالية'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.cancellation_date = timezone.now()
        booking.cancellation_reason = request.data.get('reason', '')
        booking.save()
        
        return Response({'message': 'تم إلغاء الحجز بنجاح'})
    
    except Booking.DoesNotExist:
        return Response(
            {'error': 'الحجز غير موجود'},
            status=status.HTTP_404_NOT_FOUND
        )

class CustomTripListView(generics.ListAPIView):
    """قائمة الرحلات المخصصة للمستخدم"""
    serializer_class = CustomTripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomTrip.objects.filter(user=self.request.user).order_by('-created_at')

class CustomTripDetailView(generics.RetrieveAPIView):
    """تفاصيل رحلة مخصصة"""
    serializer_class = CustomTripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomTrip.objects.filter(user=self.request.user)