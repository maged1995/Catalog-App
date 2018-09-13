#!/usr/bin/env python3
activate_this = '/var/www/FLASKAPPS/CatalogAPP/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import sys
import os
sys.path.insert(0 , '/var/www/FLASKAPPS/CatalogAPP')
sys.path.insert(1 , '/var/www/FLASKAPPS/CatalogAPP/db')
sys.stdout = open('/var/www/FLASKAPPS/CatalogAPP/output.txt', 'w')
from pages import app as application
application.secret_key = 'super_secret_key'
