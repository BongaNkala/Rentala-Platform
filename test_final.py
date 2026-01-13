import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentala.settings')
django.setup()

from django.template.loader import get_template

try:
    template = get_template('properties/properties.html')
    print("✓ Template loads successfully")
    
    # Check template attributes
    if hasattr(template, 'origin'):
        print(f"✓ Template source: {template.origin.name}")
    
    # Try to render
    rendered = template.render({})
    print(f"✓ Renders successfully ({len(rendered)} chars)")
    
    # Key checks
    checks = [
        ('sidebar', 'Sidebar'),
        ('Properties Management', 'Page title'),
        ('Total Properties', 'Stats card'),
        ('nav-item active', 'Active menu item'),
        ('Sunset Villa', 'Property data')
    ]
    
    for text, desc in checks:
        if text in rendered:
            print(f"✓ Contains {desc}")
        else:
            print(f"✗ Missing {desc}")
            
except Exception as e:
    print(f"✗ Error: {e}")
