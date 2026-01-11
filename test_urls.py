import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Test importing URLs
    from dashboard.urls import urlpatterns as dashboard_urls
    print(f"✓ Dashboard URLs: {len(dashboard_urls)} patterns")
    
    from properties.urls import urlpatterns as properties_urls
    print(f"✓ Properties URLs: {len(properties_urls)} patterns")
    
    from tenants.urls import urlpatterns as tenants_urls
    print(f"✓ Tenants URLs: {len(tenants_urls)} patterns")
    
    from payments.urls import urlpatterns as payments_urls
    print(f"✓ Payments URLs: {len(payments_urls)} patterns")
    
    from maintenance.urls import urlpatterns as maintenance_urls
    print(f"✓ Maintenance URLs: {len(maintenance_urls)} patterns")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
