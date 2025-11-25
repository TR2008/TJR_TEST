f# checkout_route.py (exemplo) -- adapte imports/nome dos modelos ao teu projeto
from flask import Blueprint, request, jsonify
from models import db, Cliente, Encomenda  # adapta aos nomes corretos do teu models.py
from datetime import datetime
import random

checkout_bp = Blueprint('checkout', __name__)

def gerar_ticket_5_digitos():
    return f"{random.randint(10000, 99999)}"

@checkout_bp.route('/api/basket/checkout', methods=['POST'])
def api_basket_checkout():
    data = request.get_json() or {}
    customer = data.get('customer') or {}
    payment_method = data.get('payment_method')
    basket = data.get('basket') or {}
    summary = data.get('summary') or {}

    # validações básicas
    required = ['nome', 'email', 'nif', 'morada', 'localidade', 'concelho', 'codigo_postal']
    missing = [f for f in required if not customer.get(f)]
    if missing:
        return jsonify({'success': False, 'message': f'Campos em falta: {", ".join(missing)}'}), 400

    # Aqui podes procurar por cliente existente (por email ou NIF) e atualizar
    try:
        # Exemplo: procurar cliente por email
        existing = Cliente.query.filter_by(email=customer.get('email')).first() if hasattr(Cliente, 'email') else None
        if existing:
            cliente = existing
            # atualiza campos se desejado
            cliente.nome = customer.get('nome')
            cliente.nif = customer.get('nif')
            cliente.morada = customer.get('morada')
            cliente.localidade = customer.get('localidade')
            cliente.concelho = customer.get('concelho')
            cliente.codigo_postal = customer.get('codigo_postal')
        else:
            cliente = Cliente(
                nome=customer.get('nome'),
                email=customer.get('email'),
                nif=customer.get('nif'),
                morada=customer.get('morada'),
                localidade=customer.get('localidade'),
                concelho=customer.get('concelho'),
                codigo_postal=customer.get('codigo_postal'),
                criado_em=datetime.utcnow()
            )
            db.session.add(cliente)
            db.session.flush()  # obtém cliente.id antes do commit

        # criar encomenda (simplificado)
        encomenda = Encomenda(
            cliente_id=cliente.id,
            items=str(basket),  # ideal serializar adequadamente (JSON) ou usar relação EncomendaItem
            total=summary.get('total', 0),
            estado='Pendente',
            metodo_pagamento=payment_method,
            criado_em=datetime.utcnow()
        )
        db.session.add(encomenda)

        # gerar ticket de 5 dígitos
        ticket = gerar_ticket_5_digitos()

        # guardamos o ticket na encomenda (se a tua tabela Encomenda tiver campo ticket)
        if hasattr(Encomenda, 'ticket'):
            encomenda.ticket = ticket

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Encomenda criada com sucesso',
            'order_id': encomenda.id,
            'ticket': ticket,
            'redirect_url': None
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500