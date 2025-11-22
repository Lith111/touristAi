from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Package, Destination, Service
from .serializers import (
    PackageListSerializer, PackageDetailSerializer, DestinationSerializer,
    ServiceSerializer, PackageSearchSerializer
)

class PackageListView(generics.ListAPIView):
    """قائمة جميع الباقات مع إمكانية البحث والتصفية"""
    queryset = Package.objects.filter(is_active=True).prefetch_related(
        'destinations', 'packagedestination_set__destination'
    )
    serializer_class = PackageListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_featured']
    search_fields = ['title', 'description', 'short_description', 'destinations__name']
    ordering_fields = ['base_price', 'duration_days', 'popularity_count', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # تصفية حسب السعر
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
            
        # تصفية حسب المدة
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        if min_duration:
            queryset = queryset.filter(duration_days__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration_days__lte=max_duration)
            
        # تصفية حسب المحافظة
        governorate = self.request.query_params.get('governorate')
        if governorate:
            queryset = queryset.filter(destinations__governorate__icontains=governorate)
            
        return queryset.distinct()

class PackageDetailView(generics.RetrieveAPIView):
    """تفاصيل باقة معينة"""
    queryset = Package.objects.filter(is_active=True).prefetch_related(
        'packagedestination_set__destination',
        'packageservice_set__service'
    )
    serializer_class = PackageDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # زيادة عداد المشاهدات
        instance.popularity_count += 1
        instance.save(update_fields=['popularity_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class DestinationListView(generics.ListAPIView):
    """قائمة الوجهات"""
    queryset = Destination.objects.filter(is_active=True)
    serializer_class = DestinationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'governorate', 'description']
    filterset_fields = ['type', 'governorate']

class ServiceListView(generics.ListAPIView):
    """قائمة الخدمات"""
    queryset = Service.objects.filter(is_active=True).select_related('destination')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'address']
    filterset_fields = ['type', 'level', 'destination']

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def package_search(request):
    """بحث متقدم في الباقات"""
    serializer = PackageSearchSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        queryset = Package.objects.filter(is_active=True)
        
        # بناء استعلام البحث
        query = Q()
        
        if data.get('query'):
            query &= Q(
                Q(title__icontains=data['query']) |
                Q(description__icontains=data['query']) |
                Q(short_description__icontains=data['query']) |
                Q(destinations__name__icontains=data['query'])
            )
            
        if data.get('package_type'):
            query &= Q(type=data['package_type'])
            
        if data.get('governorate'):
            query &= Q(destinations__governorate__icontains=data['governorate'])
            
        if data.get('min_price'):
            query &= Q(base_price__gte=data['min_price'])
            
        if data.get('max_price'):
            query &= Q(base_price__lte=data['max_price'])
            
        if data.get('min_duration'):
            query &= Q(duration_days__gte=data['min_duration'])
            
        if data.get('max_duration'):
            query &= Q(duration_days__lte=data['max_duration'])
            
        if data.get('is_featured') is not None:
            query &= Q(is_featured=data['is_featured'])
        
        packages = queryset.filter(query).distinct().prefetch_related('destinations')
        result_serializer = PackageListSerializer(packages, many=True)
        
        return Response({
            'count': packages.count(),
            'results': result_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)