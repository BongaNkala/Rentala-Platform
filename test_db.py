import os
import sys
sys.path.insert(0, '.')

os.environ['DJANGO_SETTINGS_MODULE'] = 'rentala.settings'

try:
    from django.db import connection
    connection.ensure_connection()
    print('✓ SUCCESS! Connected to MySQL database')
    print('Database:', connection.settings_dict['NAME'])
    
    # Test a simple query
    with connection.cursor() as cursor:
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()
        print(f'MySQL Version: {version[0]}')
        
except Exception as e:
    print(f'✗ Error connecting to database: {e}')
