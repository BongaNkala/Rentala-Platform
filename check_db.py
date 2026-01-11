import sys
sys.path.insert(0, '.')
from rentala import settings

print('Database Configuration:')
print('ENGINE:', settings.DATABASES['default']['ENGINE'])
print('NAME:', settings.DATABASES['default']['NAME'])
print('USER:', settings.DATABASES['default']['USER'])
print('HOST:', settings.DATABASES['default']['HOST'])
print('PORT:', settings.DATABASES['default']['PORT'])
