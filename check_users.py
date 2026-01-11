import sys
import os
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')

import django
django.setup()

from accounts.models import User

print("CHECKING USER ACCOUNTS")
print("=" * 50)

users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\nEmail: {user.email}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Superuser: {user.is_superuser}")
    print(f"Staff: {user.is_staff}")
    print(f"Active: {user.is_active}")
    print(f"Host: {user.is_host}")

print("\n" + "=" * 50)
print("SUMMARY: System is ready for your instructions.")
