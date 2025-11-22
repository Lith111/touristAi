from django.urls import path
from . import views

urlpatterns = [
    path('', views.PackageListView.as_view(), name='package-list'),
    path('<int:id>/', views.PackageDetailView.as_view(), name='package-detail'),
    path('search/advanced/', views.package_search, name='package-search'),
    path('destinations/', views.DestinationListView.as_view(), name='destination-list'),
    path('services/', views.ServiceListView.as_view(), name='service-list'),
]