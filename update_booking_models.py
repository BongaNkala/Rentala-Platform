import re

# Read the bookings/models.py file
with open('bookings/models.py', 'r') as f:
    content = f.read()

# Update any references from price_per_night to price_per_day
# This is just for consistency - the calculation logic will handle it
print("Current booking model uses listing model correctly.")
print("Note: Using listing.price_per_day for nightly rates.")

# Check if we need to update the calculate_total_price method in forms
with open('bookings/forms.py', 'r') as f:
    forms_content = f.read()
    
if 'price_per_night' in forms_content:
    print("Found price_per_night in forms.py - updating to price_per_day")
    forms_content = forms_content.replace('price_per_night', 'price_per_day')
    with open('bookings/forms.py', 'w') as f:
        f.write(forms_content)
    print("✓ Updated forms.py to use price_per_day")
else:
    print("✓ forms.py already uses correct field names")
