from flask import Blueprint, session, jsonify, request, abort, redirect, url_for, render_template
from models import Produto
from decimal import Decimal
import time
import uuid
from jinja2 import TemplateNotFound

basket_bp = Blueprint('basket', __name__)

# Helpers
def get_basket():
    return session.get('basket', {})

def calculate_total(basket):
    total = 0.0
    num_items = 0
    for item in basket.values():
        price = float(item.get('price', 0) or 0)
        qty = int(item.get('quantity', 0) or 0)
        total += price * qty
        num_items += qty
    return {'total': total, 'num_items': num_items}

def _serialize_price(value):
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except Exception:
        return 0.0

def _save_basket(basket):
    session['basket'] = basket
    session.modified = True

# Endpoints
@basket_bp.route('/api/basket', methods=['GET'])
def ver_cesto():
    if 'utilizador_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    basket = get_basket()
    summary = calculate_total(basket)
    return jsonify({'success': True, 'basket': basket, 'summary': summary})

@basket_bp.route('/api/basket/add', methods=['POST'])
def adicionar_ao_cesto():
    if 'utilizador_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    data = request.get_json() or {}
    produto_id = data.get('id')
    if produto_id is None:
        return jsonify({'success': False, 'message': 'ID do produto obrigatório'}), 400

    # Normalizar id (aceita strings enviados pelo template)
    try:
        produto_id_int = int(produto_id)
    except Exception:
        produto_id_int = None

    quantidade = 1
    try:
        quantidade = int(data.get('quantity', 1) or 1)
        if quantidade < 1:
            quantidade = 1
    except Exception:
        quantidade = 1

    produto = None
    if produto_id_int is not None:
        produto = Produto.query.get(produto_id_int)

    # Fallback útil para testes: se não houver produto no DB, aceitar name+price no body
    if not produto:
        name = data.get('name')
        price = data.get('price')
        if name is None or price is None:
            return jsonify({'success': False, 'message': 'Produto não encontrado. Forneça name e price para fallback de teste.'}), 404
        price = _serialize_price(price)
        name = str(name)
    else:
        price = _serialize_price(getattr(produto, 'preco', 0))
        name = getattr(produto, 'nome', f'Produto {produto_id}')

    produto_key = str(produto_id)  # key no session (mantém correspondência com o JS)
    basket = get_basket()
    if produto_key in basket:
        basket[produto_key]['quantity'] = int(basket[produto_key].get('quantity', 0)) + quantidade
    else:
        basket[produto_key] = {
            'name': name,
            'price': price,
            'quantity': quantidade
        }

    _save_basket(basket)
    summary = calculate_total(basket)
    return jsonify({'success': True, 'basket': basket, 'summary': summary})

@basket_bp.route('/api/basket/remove', methods=['POST'])
def remover_do_cesto():
    if 'utilizador_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    data = request.get_json() or {}
    produto_id = data.get('id')
    if produto_id is None:
        return jsonify({'success': False, 'message': 'ID do produto obrigatório'}), 400
    remover_tudo = bool(data.get('remove_all', False))

    produto_key = str(produto_id)
    basket = get_basket()
    if produto_key not in basket:
        return jsonify({'success': False, 'message': 'Item não está no cesto'}), 404

    if remover_tudo or int(basket[produto_key].get('quantity', 1)) <= 1:
        del basket[produto_key]
    else:
        basket[produto_key]['quantity'] = int(basket[produto_key].get('quantity', 1)) - 1

    _save_basket(basket)
    summary = calculate_total(basket)
    return jsonify({'success': True, 'basket': basket, 'summary': summary})

@basket_bp.route('/api/basket/clear', methods=['POST'])
def clear_basket():
    if 'utilizador_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    session.pop('basket', None)
    session.modified = True
    return jsonify({'success': True, 'basket': {}, 'summary': {'total': 0.0, 'num_items': 0}})

@basket_bp.route('/api/basket/checkout', methods=['POST'])
def checkout():
    if 'utilizador_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401

    basket = get_basket()
    if not basket:
        return jsonify({'success': False, 'message': 'Cesto vazio'}), 400

    summary = calculate_total(basket)
    order = {
        'order_id': str(uuid.uuid4()),
        'created_at': int(time.time()),
        'user_id': session.get('utilizador_id'),
        'items': basket,
        'summary': summary
    }

    # Em produção: gravar no DB (Order model). Aqui apenas guardamos em sessão.
    session['last_order'] = order
    session.pop('basket', None)
    session.modified = True

    return jsonify({'success': True, 'message': 'Encomenda criada', 'order': order, 'basket': {}, 'summary': {'total': 0.0, 'num_items': 0}})

# --------------------------------------------------------
# Nova rota: /detalhes  -> redireciona para /detalhes/<id> (1..11)
# Aceita query param "id" ou "n". Se não fornecido, redireciona para id=1.
# --------------------------------------------------------
@basket_bp.route('/detalhes')
def detalhes_redirect():
    id_param = request.args.get('id') or request.args.get('n')
    if id_param:
        try:
            id_int = int(id_param)
        except Exception:
            abort(404)
    else:
        id_int = 1  # default

    if not (1 <= id_int <= 11):
        abort(404)

    return redirect(url_for('basket.detalhes', id=id_int))

@basket_bp.route('/detalhes/<int:id>')
def detalhes(id):
    # procura templates/paginas/detalhes_<id>.html
    template_name = f'paginas/detalhes_{id}.html'
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404)