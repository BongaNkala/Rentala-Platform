import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Test importing each model
    from properties.models import Property
    print("✓ Property model imported")
    
    from tenants.models import Tenant
    print("✓ Tenant model imported")
    
    from payments.models import Payment
    print("✓ Payment model imported")
    
    from maintenance.models import MaintenanceRequest
    print("✓ MaintenanceRequest model imported")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
