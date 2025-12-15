from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_wtf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    # força a app a usar a pasta 'templates' e 'static' do projecto
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Secret key idealmente via CONFIG / variáveis ambiente
    app.config.setdefault('SECRET_KEY', 'algum_valor_secreto')

    # Sessão / cookie options — ajuste para produção
    # Se o frontend e API estiverem no mesmo domínio use 'Lax' e SECURE=False (desenvolvimento)
    # Se estiverem em domínios diferentes use 'None' E SECURE=True (HTTPS) e no frontend fetch credentials:'include'
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('SESSION_COOKIE_SECURE', False)

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    # Importar e registar blueprints
    from routes.auth import auth_bp
    from routes.cliente import cliente_bp
    from routes.produto import produto_bp
    from routes.paginas import paginas_bp
    from routes.basket import basket_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(paginas_bp)
    app.register_blueprint(basket_bp)

    return app


app = create_app()


# Define index route after app creation to avoid NameError
@app.route('/')
def index():
    return "Flask app is running! Visit /login to start."


if __name__ == '__main__':
    app.run(debug=True)