"""
WSGI entry point for Passenger (cPanel)

Este ficheiro é o ponto de entrada para o Passenger no cPanel.
O Passenger procura pela variável 'application' neste ficheiro.
"""

import sys
import os

# Adicionar o diretório da aplicação ao path do Python
INTERP = os.path.expanduser("~/virtualenv/public_html/3.9/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Importar a aplicação Flask
from app import app as application

# Para debug (remover em produção)
if __name__ == "__main__":
    application.run()
