# passenger_wsgi.py — interface WSGI para cPanel/Passenger
# Deve expor a variável 'application'

import sys
import os

# Se necessário adicione o path da app (ajuste conforme o seu usuário)
# Por exemplo: sys.path.insert(0, "/home/SEU_USUARIO/myflaskapp")

from app import app as application  # importa a Flask app e nomeia 'application