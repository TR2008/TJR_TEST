import sys
import os

# Add your project directory to the sys.path
project_home = '/home/username/hvacsolution81.com'  # Update with your actual cPanel path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # CHANGE THIS in cPanel
# os.environ['DATABASE_URL'] = 'your-database-url-here'  # Optional: set if using MySQL/PostgreSQL

from app import app as application

# Optional: configure logging
# import logging
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
