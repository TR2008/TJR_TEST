from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # valores default (em produção usar VARS de ambiente)
    app.config.setdefault('SECRET_KEY', 'algum_valor_secreto')
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('SESSION_COOKIE_SECURE', False)

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    # registar blueprints (ajuste nomes se necessário)
    try:
        from routes.auth import auth_bp
        from routes.cliente import cliente_bp
        from routes.produto import produto_bp
        from routes.paginas import paginas_bp
        from routes.basket import basket_bp
    except Exception:
        # se alguns blueprints não existirem, ignore e continue (útil para testes)
        auth_bp = None
        paginas_bp = None
        cliente_bp = None
        produto_bp = None
        basket_bp = None

    if auth_bp:
        app.register_blueprint(auth_bp)
    if cliente_bp:
        app.register_blueprint(cliente_bp)
    if produto_bp:
        app.register_blueprint(produto_bp)
    if paginas_bp:
        app.register_blueprint(paginas_bp)
    if basket_bp:
        app.register_blueprint(basket_bp)

    return app

# criar a instância da app para execução direta e para passenger_wsgi
app = create_app()

# Rota de index definida depois de 'app' existir para evitar NameError
@app.route('/')
def index():
    return "HVAC Solution - app em produção"

if __name__ == '__main__':
    app.run(debug=True)