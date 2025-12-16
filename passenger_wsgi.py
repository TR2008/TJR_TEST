"""
Ficheiro WSGI para executar a aplicação Flask com Passenger no cPanel.

Este ficheiro é o ponto de entrada da aplicação quando executada pelo Passenger.
O Passenger carrega este módulo e procura pela variável 'application' (protocolo WSGI).
"""

import sys
import os

# Caminho absoluto da pasta onde está a aplicação
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Adicionar o diretório da aplicação ao sys.path
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Log de debug para ajudar a diagnosticar problemas
print(f"[passenger_wsgi.py] WSGI iniciado", file=sys.stderr)
print(f"[passenger_wsgi.py] Diretório da app: {APP_DIR}", file=sys.stderr)
print(f"[passenger_wsgi.py] Python sys.path: {sys.path}", file=sys.stderr)

try:
    # Importar a aplicação Flask
    # Assumindo que o ficheiro principal é 'app.py' e a variável Flask é 'app'
    from app import app as application
    
    print(f"[passenger_wsgi.py] ✓ Aplicação Flask importada com sucesso", file=sys.stderr)
    print(f"[passenger_wsgi.py] ✓ Aplicação WSGI: {application}", file=sys.stderr)
    
except ImportError as e:
    print(f"[passenger_wsgi.py] ✗ ERRO ao importar aplicação: {e}", file=sys.stderr)
    print(f"[passenger_wsgi.py] Verifique:", file=sys.stderr)
    print(f"  1. O ficheiro 'app.py' existe no diretório: {APP_DIR}", file=sys.stderr)
    print(f"  2. A variável Flask chama-se 'app' em app.py", file=sys.stderr)
    print(f"  3. Todas as dependências estão instaladas no virtualenv", file=sys.stderr)
    print(f"  4. O virtualenv está ativo no Passenger (configuração .htaccess)", file=sys.stderr)
    
    # Re-lançar a exceção para que o Passenger mostre o erro
    raise

except Exception as e:
    print(f"[passenger_wsgi.py] ✗ ERRO inesperado: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise

# O Passenger procura pela variável 'application' (protocolo WSGI)
# Se chegámos aqui, a aplicação foi importada com sucesso
