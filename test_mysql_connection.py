import sys
import os
sys.path.insert(0, '.')

# Try different MySQL configurations
configs = [
    {'PASSWORD': ''},  # Empty password
    {'PASSWORD': 'password'},
    {'PASSWORD': 'root'},
    {'PASSWORD': 'admin'},
    {'PASSWORD': 'Password123'},
    {'PASSWORD': 'mysql'},
]

for config in configs:
    try:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'rentala.settings'
        
        # Temporarily modify settings
        from rentala import settings
        original_password = settings.DATABASES['default']['PASSWORD']
        settings.DATABASES['default']['PASSWORD'] = config['PASSWORD']
        
        # Test connection
        from django.db import connection
        connection.ensure_connection()
        print(f"✓ SUCCESS! Password works: '{config['PASSWORD']}'")
        break
    except Exception as e:
        if "Access denied" in str(e):
            print(f"✗ Access denied with password: '{config['PASSWORD']}'")
        else:
            print(f"✗ Error with password '{config['PASSWORD']}': {str(e)[:100]}")
