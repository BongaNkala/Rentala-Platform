from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    
    # Dashboard and Management URLs
    path('dashboard/', include('dashboard.urls')),
    path('properties/', include('properties.urls')),
    path('tenants/', include('tenants.urls')),
    path('payments/', include('payments.urls')),
    path('maintenance/', include('maintenance.urls')),
    
    # Authentication URLs - ADDED THIS LINE
    path('accounts/', include('accounts.urls')),
    
    # Original app URLs (for rental marketplace)
    path('listings/', include('listings.urls')),
    path('bookings/', include('bookings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  
