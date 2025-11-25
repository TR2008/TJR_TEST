from .cliente import cliente_bp
from .basket import basket_bp
from .paginas import paginas_bp
from routes.produto import produto_bp



def register_blueprints(app):


    app.register_blueprint(cliente_bp)
    app.register_blueprint(basket_bp)
    app.register_blueprint(paginas_bp)
    app.register_blueprint(produto_bp)
