from flask import Flask
from config import Config
from flask_wtf import CSRFProtect

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

    # Import db from models and initialize
    from models import db
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    # Importar e registar blueprints com try/except para facilitar testes locais
    blueprints = [
        ('routes.auth', 'auth_bp'),
        ('routes.cliente', 'cliente_bp'),
        ('routes.produto', 'produto_bp'),
        ('routes.paginas', 'paginas_bp'),
        ('routes.basket', 'basket_bp'),
    ]
    
    for module_name, bp_name in blueprints:
        try:
            module = __import__(module_name, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint)
            print(f"✓ Registered blueprint: {bp_name}")
        except (ImportError, AttributeError) as e:
            print(f"✗ Could not register blueprint {bp_name}: {e}")

    # Add a simple index route
    @app.route('/')
    def index():
        return "Flask Application is running! Visit /login to access the application."

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)