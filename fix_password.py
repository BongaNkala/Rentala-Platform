import re

# Read the settings file
with open('rentala/settings.py', 'r') as f:
    content = f.read()

print("Before update:")
print(re.search(r"'PASSWORD':\s*'.*?'", content).group() if re.search(r"'PASSWORD':\s*'.*?'", content) else "No password found")

# Find and replace the password
pattern = r"('PASSWORD':\s*)'.*?'"
new_content = re.sub(pattern, r"\1'Siya-Samkelo1st'", content)

# Write back
with open('rentala/settings.py', 'w') as f:
    f.write(new_content)

print("After update:")
print(re.search(r"'PASSWORD':\s*'.*?'", new_content).group())
print("✓ Password updated successfully!")
