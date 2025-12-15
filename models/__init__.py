from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Utilizador(db.Model):
    __tablename__ = 'utilizador'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, senha):
        """Gera hash da senha"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Utilizador {self.email}>'


class Produto(db.Model):
    __tablename__ = 'produto'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100))
    preco = db.Column(db.Float, nullable=False, default=0.0)
    descricao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'


class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    nif = db.Column(db.String(20), unique=True, index=True)
    morada = db.Column(db.String(200))
    localidade = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    concelho1 = db.Column(db.String(100))
    concelho2 = db.Column(db.String(100))
    aniversario = db.Column(db.Date)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com encomendas
    encomendas = db.relationship('Encomenda', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Encomenda(db.Model):
    __tablename__ = 'encomenda'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    items = db.Column(db.Text)  # JSON string com items da encomenda
    total = db.Column(db.Float, nullable=False, default=0.0)
    estado = db.Column(db.String(50), default='Pendente')
    metodo_pagamento = db.Column(db.String(50))
    ticket = db.Column(db.String(100), unique=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Encomenda {self.id} - {self.estado}>'
