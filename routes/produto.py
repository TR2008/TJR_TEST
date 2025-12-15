from flask import Blueprint, request, jsonify, session, redirect, url_for
from models import Produto, db

produto_bp = Blueprint('produto', __name__)

@produto_bp.route('/inserir_preco', methods=['POST'])
def inserir_preco():

    if 'utilizador_id' not in session:
        if request.is_json:
            return jsonify({'erro': 'Não autenticado'}), 401
        return redirect(url_for('auth.login'))

    data = request.get_json(silent=True) or {}
    nome = data.get('nome')
    categoria = data.get('categoria')
    preco = data.get('preco')

    if not nome or not categoria or preco is None:
        return jsonify({'erro': 'Todos os campos são obrigatórios: nome, categoria, preco'}), 400

    nome = str(nome).strip()
    categoria = str(categoria).strip()
    if not nome:
        return jsonify({'erro': 'Nome inválido'}), 400
    if not categoria:
        return jsonify({'erro': 'Categoria inválida'}), 400

    try:
        preco = float(preco)
    except (TypeError, ValueError):
        return jsonify({'erro': 'Preço inválido'}), 400

    if preco < 0:
        return jsonify({'erro': 'Preço não pode ser negativo'}), 400

    produto_existente = Produto.query.filter_by(nome=nome, categoria=categoria).first()
    if produto_existente:
        return jsonify({'erro': 'Produto já existe', 'produto_id': produto_existente.id}), 409

    novo_produto = Produto(nome=nome, categoria=categoria, preco=preco)
    db.session.add(novo_produto)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao gravar o produto', 'detalhes': str(e)}), 500

    item = {
        'id': getattr(novo_produto, 'id', None),
        'nome': nome,
        'categoria': categoria,
        'preco': preco
    }

    return jsonify({'mensagem': 'Produto inserido com sucesso!', 'item': item}), 201


@produto_bp.route('/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_preco(produto_id):
    """
    Atualiza o preço de um produto existente.
    Espera JSON com chave 'preco'.
    """
    if 'utilizador_id' not in session:
        if request.is_json:
            return jsonify({'erro': 'Não autenticado'}), 401
        return redirect(url_for('auth.login'))

    data = request.get_json(silent=True) or {}
    if 'preco' not in data:
        return jsonify({'erro': 'Campo preco é obrigatório'}), 400

    try:
        novo_preco = float(data.get('preco'))
    except (TypeError, ValueError):
        return jsonify({'erro': 'Preço inválido'}), 400

    if novo_preco < 0:
        return jsonify({'erro': 'Preço não pode ser negativo'}), 400

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({'erro': 'Produto não encontrado'}), 404

    produto.preco = novo_preco
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao actualizar o produto', 'detalhes': str(e)}), 500

    return jsonify({
        'mensagem': 'Preço actualizado com sucesso',
        'item': {
            'id': produto_id,
            'nome': getattr(produto, 'nome', None),
            'categoria': getattr(produto, 'categoria', None),
            'preco': novo_preco
        }
    }), 200