import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import your Flask application instance (named 'app' in app.py)
from app import app as application