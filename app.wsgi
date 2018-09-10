#!/usr/bin/python3
activate_this = '/var/www/FLASKAPPS/CatalogAPP/pages.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
from catapp import app as application
import sys
sys.path.insert(0,"/var/www/FLASKAPPS/CatalogAPP")
