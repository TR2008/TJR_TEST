from flask import Blueprint, request, jsonify, session, redirect, url_for
from models import Cliente, db
from datetime import datetime

cliente_bp = Blueprint('cliente', __name__)


@cliente_bp.route('/cadastro', methods=['POST'])
def cadastro():
    if 'utilizador' not in session:
        return jsonify({'erro': 'Não autenticado'}), 401

    data = request.get_json()
    try:
        novo_cliente = Cliente(
            nome=data['nome'],
            nif=data['nif'],
            morada=data['morada'],
            aniversario=datetime.strptime(data['aniversario'], '%Y-%m-%d').date()
        )
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({'mensagem': 'Cliente cadastrado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


@cliente_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    if 'utilizador' not in session:
        return redirect(url_for('auth.login'))

    clientes = Cliente.query.all()
    resultado = [
        {
            'id': c.id,
            'nome': c.nome,
            'nif': c.nif,
            'morada': c.morada,
            'aniversario': c.aniversario.strftime('%Y-%m-%d')
        } for c in clientes
    ]
    return jsonify(resultado)