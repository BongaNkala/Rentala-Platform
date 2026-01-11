from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # User booking URLs
    path('', views.BookingListView.as_view(), name='list'),
    path('<uuid:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<uuid:pk>/payment/', views.BookingPaymentView.as_view(), name='payment'),
    path('<uuid:pk>/cancel/', views.cancel_booking, name='cancel'),
    
    # Create booking for a specific listing
    path('listing/<uuid:listing_id>/create/', views.BookingCreateView.as_view(), name='create'),
    
    # Host booking management
    path('host/', views.HostBookingsListView.as_view(), name='host_bookings'),
    path('<uuid:pk>/confirm/', views.confirm_booking, name='confirm'),
    
    # API endpoints
    path('api/check-availability/<uuid:listing_id>/', views.check_availability, name='check_availability'),
]
