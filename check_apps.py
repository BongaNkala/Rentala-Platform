import sys
sys.path.insert(0, '.')
from rentala import settings

print("Current INSTALLED_APPS:")
for app in settings.INSTALLED_APPS:
    print(f"  - {app}")

required_apps = ['dashboard', 'properties', 'tenants', 'payments', 'maintenance']
print("\nChecking required apps:")
for app in required_apps:
    if app in settings.INSTALLED_APPS:
        print(f"✓ {app}")
    else:
        print(f"✗ {app} - NEEDS TO BE ADDED")
