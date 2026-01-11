#!/usr/bin/env python3

with open('properties/templates/properties/properties.html', 'r') as f:
    lines = f.readlines()

# Find first and second occurrence of {% block content %}
first_block = None
second_block = None
for i, line in enumerate(lines):
    if '{% block content %}' in line:
        if first_block is None:
            first_block = i
        else:
            second_block = i
            break

if second_block:
    print(f"Found duplicate blocks at lines {first_block} and {second_block}")
    # Keep everything up to the second block
    new_content = lines[:second_block]
    # Add closing tags if needed
    new_content.append('{% endblock %}\n')
    
    with open('properties/templates/properties/properties.html', 'w') as f:
        f.writelines(new_content)
    print("Removed duplicate content block")
else:
    print("No duplicate found")
