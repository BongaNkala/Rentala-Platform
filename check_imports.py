import sys
sys.path.insert(0, '.')

try:
    import crispy_forms
    print(f'✓ crispy_forms imported successfully: {crispy_forms.__version__}')
except ImportError as e:
    print(f'✗ Error importing crispy_forms: {e}')

try:
    import crispy_bootstrap5
    print(f'✓ crispy_bootstrap5 imported successfully')
except ImportError as e:
    print(f'✗ Error importing crispy_bootstrap5: {e}')

try:
    from rentala import settings
    print('✓ Successfully imported settings')
    
    # Check Django setup
    import django
    django.setup()
    print('✓ Django setup completed')
    
    # Check if apps are loaded
    from django.apps import apps
    print(f'✓ Total apps loaded: {len(apps.get_app_configs())}')
    
except Exception as e:
    print(f'✗ Error: {e}')
