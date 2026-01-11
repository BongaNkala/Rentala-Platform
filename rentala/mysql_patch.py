# Patch for Django MySQL backend to accept pymysql
import django
from django.db.backends.mysql.base import DatabaseWrapper

# Monkey-patch the version check
import pymysql
pymysql.version_info = (2, 2, 7, 'final', 0)  # Fake version info
pymysql.__version__ = "2.2.7"

# Apply the patch
pymysql.install_as_MySQLdb()
