import sys
import os

# Add your project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import your Flask app
from app import app as application  # Replace `app` with the name of your Flask app variable