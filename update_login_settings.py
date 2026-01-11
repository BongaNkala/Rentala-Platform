import re

# Read settings.py
with open('rentala/settings.py', 'r') as f:
    content = f.read()

# Check if LOGIN_URL is set
if 'LOGIN_URL' not in content:
    print("Adding LOGIN_URL to settings...")
    
    # Find a good place to insert (near other URL settings)
    pattern = r"LOGIN_REDIRECT_URL\s*=\s*"
    match = re.search(pattern, content)
    
    if match:
        insert_pos = match.end()
        login_config = '''
# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
'''
        # Find the end of the LOGIN_REDIRECT_URL line
        line_end = content.find('\n', insert_pos)
        new_content = content[:line_end] + login_config + content[line_end:]
        
        with open('rentala/settings.py', 'w') as f:
            f.write(new_content)
        print("✅ Added login configuration")
    else:
        print("❌ Could not find LOGIN_REDIRECT_URL in settings")
else:
    print("✅ Login configuration already exists")
