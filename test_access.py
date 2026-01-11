import requests

def test_url(name, url):
    try:
        response = requests.get(f'http://localhost:8000{url}', timeout=3)
        return f"{name}: {'✅ OK' if response.status_code == 200 else f'⚠️ Status {response.status_code}'}"
    except Exception as e:
        return f"{name}: ❌ Error ({str(e)[:30]})"

print("Testing Rentala Pages...")
print("=" * 40)

pages = [
    ("Home", "/"),
    ("Dashboard", "/dashboard/"),
    ("Properties", "/properties/"),
    ("Tenants", "/tenants/"),
    ("Payments", "/payments/"),
    ("Maintenance", "/maintenance/"),
]

for name, url in pages:
    result = test_url(name, url)
    print(result)

print("=" * 40)
print("Test complete!")
