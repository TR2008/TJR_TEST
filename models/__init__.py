from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Utilizador(db.Model):
    __tablename__ = 'utilizador'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Utilizador {self.email}>'


class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=True)
    preco = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Produto {self.nome}>'


class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    nif = db.Column(db.String(20), nullable=True)
    morada = db.Column(db.String(200), nullable=True)
    localidade = db.Column(db.String(100), nullable=True)
    codigo_postal = db.Column(db.String(20), nullable=True)
    concelho1 = db.Column(db.String(100), nullable=True)
    concelho2 = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    aniversario = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


# Optional: Encomenda model for order tracking (referenced in paginas.py)
class Encomenda(db.Model):
    __tablename__ = 'encomenda'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    items = db.Column(db.Text, nullable=True)  # JSON string or serialized basket
    total = db.Column(db.Float, nullable=True)
    estado = db.Column(db.String(50), nullable=True)  # Pendente, Aguardando, Concluido, etc.
    metodo_pagamento = db.Column(db.String(50), nullable=True)
    ticket = db.Column(db.String(100), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Encomenda {self.id}>'
