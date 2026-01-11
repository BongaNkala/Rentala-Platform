import sys
import os
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')

import django
django.setup()

from django.conf import settings

print("=== AUTHENTICATION SETTINGS ===")
print(f"LOGIN_URL: {settings.LOGIN_URL}")
print(f"LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
print(f"LOGOUT_REDIRECT_URL: {getattr(settings, 'LOGOUT_REDIRECT_URL', 'Not set')}")

print("\n=== INSTALLED APPS ===")
if 'django.contrib.auth' in settings.INSTALLED_APPS:
    print("✅ django.contrib.auth is installed")
else:
    print("❌ django.contrib.auth is NOT installed")

print("\n=== MIDDLEWARE ===")
if 'django.contrib.auth.middleware.AuthenticationMiddleware' in settings.MIDDLEWARE:
    print("✅ AuthenticationMiddleware is in middleware")
else:
    print("❌ AuthenticationMiddleware is NOT in middleware")
