import sys
import os

# IMPORTANT: Update the paths below before deploying to cPanel
# Add your project directory to the sys.path
project_home = '/home/username/hvacsolution81.com'  # CHANGE THIS: Update with your actual cPanel path (e.g., /home/cpanel_username/hvacsolution81.com)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# IMPORTANT: Set environment variables for production
# Option 1: Set via cPanel's "Setup Python App" interface (recommended)
# Option 2: Set here (less secure, but functional)
# Generate a secure SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"
os.environ.setdefault('SECRET_KEY', 'CHANGE-THIS-TO-A-SECURE-SECRET-KEY')  # CHANGE THIS: Replace with a strong random key
# os.environ.setdefault('DATABASE_URL', 'mysql://user:password@localhost/dbname')  # Optional: uncomment and set if using MySQL/PostgreSQL

from app import app as application

# Optional: configure logging for debugging
# import logging
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

