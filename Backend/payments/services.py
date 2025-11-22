import json
import random
from django.utils import timezone
from .models import Payment

class PaymentProcessor:
    """خدمة معالجة الدفعات (محاكاة)"""
    
    @staticmethod
    def process_payment(payment):
        """معالجة الدفعة (محاكاة لبوابة دفع)"""
        try:
            # محاكاة اتصال ببوابة الدفع
            # في الواقع، هنا سيتم الاتصال ببوابة الدفع الحقيقية
            
            # محاكاة نجاح الدفع بنسبة 80%
            if random.random() < 0.8:
                return PaymentProcessor._simulate_successful_payment(payment)
            else:
                return PaymentProcessor._simulate_failed_payment(payment)
                
        except Exception as e:
            return PaymentProcessor._simulate_failed_payment(payment, str(e))
    
    @staticmethod
    def _simulate_successful_payment(payment):
        """محاكاة دفعة ناجحة"""
        transaction_id = f"TXN{payment.payment_number}{random.randint(1000, 9999)}"
        
        payment.status = 'completed'
        payment.transaction_id = transaction_id
        payment.payment_date = timezone.now()
        payment.payment_gateway_response = {
            'status': 'success',
            'transaction_id': transaction_id,
            'message': 'تمت العملية بنجاح',
            'timestamp': timezone.now().isoformat()
        }
        payment.save()
        
        # تحديث حالة الحجز
        booking = payment.booking
        booking.status = 'paid'
        booking.save()
        
        return True
    
    @staticmethod
    def _simulate_failed_payment(payment, error_message="فشل في المعالجة"):
        """محاكاة دفعة فاشلة"""
        payment.status = 'failed'
        payment.payment_gateway_response = {
            'status': 'failed',
            'error_message': error_message,
            'timestamp': timezone.now().isoformat()
        }
        payment.save()
        return False
    
    @staticmethod
    def process_refund(payment, refund_amount, reason):
        """معالجة استرداد الأموال"""
        if not payment.can_refund:
            return False, "لا يمكن استرداد هذه الدفعة"
        
        if refund_amount > payment.amount:
            return False, "مبلغ الاسترداد أكبر من المبلغ المدفوع"
        
        # محاكاة عملية الاسترداد
        payment.refund_amount = refund_amount
        payment.refund_date = timezone.now()
        payment.refund_reason = reason
        payment.status = 'refunded'
        payment.save()
        
        # تحديث حالة الحجز
        booking = payment.booking
        booking.status = 'refunded'
        booking.save()
        
        return True, "تم استرداد المبلغ بنجاح"