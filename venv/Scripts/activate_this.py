import os
import sys
import site

# Directory of the virtual environment
VENV_DIR = '/home/mwhlrr/NCRManager/venv'

# The site-packages directory for the virtual environment
site_packages = os.path.join(VENV_DIR, 'lib/python3.10/site-packages')

# Add the site-packages directory to sys.path
sys.path.insert(0, site_packages)

# Set environment variables to point to the virtual environment
os.environ['VIRTUAL_ENV'] = VENV_DIR
os.environ['PATH'] = os.path.join(VENV_DIR, 'bin') + os.pathsep + os.environ['PATH']

# Prepend the bin directory to sys.path so that the virtual environment's Python executable is used
sys.path.insert(0, os.path.join(VENV_DIR, 'bin'))

# Activate the virtual environment
site.addsitedir(site_packages)
