activate_this = '/var/www/FLASKAPPS/CatalogAPP/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0 , '/var/www/FLASKAPPS/CatalogAPP')
from pages import app as application
