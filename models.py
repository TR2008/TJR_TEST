from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Utilizador(db.Model):
    __tablename__ = 'utilizador'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    morada = db.Column(db.String(200))
    localidade = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    concelho1 = db.Column(db.String(100))
    concelho2 = db.Column(db.String(100))
    nif = db.Column(db.String(20))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Encomenda(db.Model):
    __tablename__ = 'encomenda'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    items = db.Column(db.Text)
    total = db.Column(db.Float)
    estado = db.Column(db.String(50), default='Pendente')
    metodo_pagamento = db.Column(db.String(50))
    ticket = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
