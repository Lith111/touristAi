from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('<str:payment_number>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('initiate/<str:booking_number>/', views.initiate_payment, name='initiate-payment'),
    path('refund/', views.request_refund, name='request-refund'),
    path('methods/', views.payment_methods, name='payment-methods'),
    path('currencies/', views.currencies, name='currencies'),
    path('webhook/', views.payment_webhook, name='payment-webhook'),
    path('gateways/', views.PaymentGatewayListView.as_view(), name='payment-gateways'),
]