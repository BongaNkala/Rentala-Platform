#!/bin/bash

echo "Fixing all URL configurations..."

# Fix tenants URLs
cat > tenants/urls.py << 'URL_EOF'
from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:tenant_id>/', views.TenantDetailView.as_view(), name='detail'),
    path('create/', views.TenantCreateView.as_view(), name='create'),
]
URL_EOF
echo "✓ Fixed tenants/urls.py"

# Fix payments URLs
cat > payments/urls.py << 'URL_EOF'
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:payment_id>/', views.PaymentDetailView.as_view(), name='detail'),
    path('create/', views.PaymentCreateView.as_view(), name='create'),
]
URL_EOF
echo "✓ Fixed payments/urls.py"

# Fix maintenance URLs
cat > maintenance/urls.py << 'URL_EOF'
from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:request_id>/', views.MaintenanceDetailView.as_view(), name='detail'),
    path('create/', views.MaintenanceCreateView.as_view(), name='create'),
]
URL_EOF
echo "✓ Fixed maintenance/urls.py"

# Fix properties URLs (complete it)
cat > properties/urls.py << 'URL_EOF'
from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:property_id>/', views.PropertyDetailView.as_view(), name='detail'),
    path('create/', views.PropertyCreateView.as_view(), name='create'),
]
URL_EOF
echo "✓ Fixed properties/urls.py"

# Fix dashboard URLs (update view name)
cat > dashboard/urls.py << 'URL_EOF'
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('forecasting/', views.ForecastingView.as_view(), name='forecasting'),
]
URL_EOF
echo "✓ Fixed dashboard/urls.py"

echo -e "\n✅ ALL URLS FIXED!"
echo "Starting server now..."
