import sys
import os
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')

import django
django.setup()

from accounts.models import User

print("CREATING SUPERUSER ACCOUNT")
print("=" * 50)

# Check if exists
try:
    user = User.objects.get(email='bonga@rentala.com')
    print(f"✅ Account already exists: {user.email}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"   Staff: {user.is_staff}")
    
    # Make sure it's a superuser
    if not user.is_superuser:
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("✅ Upgraded to superuser")
        
except User.DoesNotExist:
    # Create superuser
    user = User.objects.create_superuser(
        email='bonga@rentala.com',
        password='bonga123',
        first_name='Bonga',
        last_name='Mthembu'
    )
    print(f"✅ Created superuser: {user.email}")
    print(f"   Password: bonga123")

print("\n" + "=" * 50)
print("ADMIN LOGIN:")
print("URL: http://localhost:8000/admin/")
print("Email: bonga@rentala.com")
print("Password: bonga123")
print("\nREGULAR USER:")
print("Email: guest@rentala.com")
print("Password: guest123")
print("\nHOST USER:")
print("Email: host@rentala.com")
print("Password: host123")
