import re

# Read the file
with open('rentala/settings.py', 'r') as f:
    content = f.read()

# Remove the duplicate apps outside the list
# Find everything from INSTALLED_APPS to MIDDLEWARE
pattern = r'(INSTALLED_APPS = \[.*?\n\])(.*?)(MIDDLEWARE = \[)'
match = re.search(pattern, content, re.DOTALL)

if match:
    installed_apps = match.group(1)
    between = match.group(2)
    middleware = match.group(3)
    
    # Clean up the between part - remove any stray app declarations
    clean_between = re.sub(r"\s*'[a-z_]+',\n", '', between)
    
    # Create new content
    new_content = content.replace(match.group(0), installed_apps + clean_between + middleware)
    
    # Write back
    with open('rentala/settings.py', 'w') as f:
        f.write(new_content)
    
    print('Cleaned up INSTALLED_APPS section')
else:
    print('Could not find INSTALLED_APPS section')
