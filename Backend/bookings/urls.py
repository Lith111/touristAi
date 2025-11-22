from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking-list'),
    path('create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('<str:booking_number>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('<str:booking_number>/cancel/', views.cancel_booking, name='booking-cancel'),
    path('custom-trips/', views.CustomTripListView.as_view(), name='custom-trip-list'),
    path('custom-trips/<int:pk>/', views.CustomTripDetailView.as_view(), name='custom-trip-detail'),
]