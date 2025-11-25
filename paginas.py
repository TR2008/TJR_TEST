from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app, abort
import random
import datetime
import re
import uuid
from jinja2 import TemplateNotFound

paginas_bp = Blueprint('paginas', __name__)

@paginas_bp.route('/dashboard')
def dashboard():
    # Ajuste a lógica de sessão conforme necessário (ex.: permitir anónimo)
    if 'utilizador' in session:
        return redirect(url_for('auth.login'))
    return render_template('paginas/dashboard.html')

@paginas_bp.route('/contactos')
def contactos():
    if 'utilizador' in session:
        return redirect(url_for('auth.login'))
    return render_template('paginas/contactos.html')

@paginas_bp.route('/produtos')
@paginas_bp.route('/produtos_html')
def produtos_html():
    # Rota que serve a página de produtos (endpoint: paginas.produtos_html)
    if 'utilizador' in session:
        return redirect(url_for('auth.login'))
    from models import Produto  # opcional: carregar produtos do BD no futuro
    # Se quiser passar produtos do BD ao template: produtos = Produto.query.all()
    return render_template('paginas/produtos.html')

@paginas_bp.route('/servicos')
def servicos_html():
    if 'utilizador' in session:
        return redirect(url_for('auth.login'))
    return render_template('paginas/servicos.html')

@paginas_bp.route('/politica-privacidade', endpoint='politica_privacidade')
def politica_privacidade():
    return render_template('paginas/politica_privacidade.html')

@paginas_bp.route('/termos-uso', endpoint='termos_uso')
def sobre():
    return render_template('paginas/sobre.html')

@paginas_bp.route('/referencias', endpoint='referencias')
def referencias():
    # Permitir apenas autenticados (ajuste conforme necessário)
    if 'utilizador' not in session:
        return redirect(url_for('auth.login'))
    return render_template('paginas/referencias.html')

# --------------------------------------------------------
# Nova rota: /detalhes  -> redireciona para /detalhes/<id>
# Aceita query param "id" ou "n". Se não fornecido, redireciona para id=1.
# Valida que id esteja entre 1 e 11.
# --------------------------------------------------------
@paginas_bp.route('/detalhes')
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

    return redirect(url_for('paginas.detalhes', id=id_int))

# --------------------------------------------------------
# Helpers e endpoints para MB / tickets (mantidos)
# --------------------------------------------------------
def _validate_phone(value):
    if not value:
        return False
    cleaned = re.sub(r'[^\d+]', '', value)
    return len(re.sub(r'\D', '', cleaned)) >= 9

def _validate_nif(value):
    if not value:
        return False
    return bool(re.fullmatch(r'\d{9}', value))

def _generate_mb_reference():
    ref = ''.join(str(random.randint(0, 9)) for _ in range(9))
    return f"{ref[0:3]} {ref[3:6]} {ref[6:9]}"

def _generate_entidade():
    return ''.join(str(random.randint(0, 9)) for _ in range(5))

_simulated_tickets = {}

@paginas_bp.route('/api/payment/multibanco', methods=['POST'])
def api_payment_multibanco():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "message": "JSON inválido"}), 400

    customer = payload.get('customer') or {}
    telefone = (customer.get('telefone') or customer.get('telefone_mobile') or customer.get('phone') or '').strip()
    nif = (customer.get('nif') or '').strip()

    if not telefone:
        return jsonify({"success": False, "message": "Telefone é obrigatório"}), 400
    if not _validate_phone(telefone):
        return jsonify({"success": False, "message": "Telefone inválido"}), 400

    if not nif:
        return jsonify({"success": False, "message": "NIF é obrigatório"}), 400
    if not _validate_nif(nif):
        return jsonify({"success": False, "message": "NIF inválido (9 dígitos)"}), 400

    amount = payload.get('amount')
    try:
        valor = float(amount) if amount is not None else float(payload.get('basket', {}).get('summary', {}).get('total', 0))
    except Exception:
        return jsonify({"success": False, "message": "Valor (amount) inválido"}), 400

    entidade = _generate_entidade()
    referencia = _generate_mb_reference()
    validade_dt = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    validade_iso = validade_dt.replace(microsecond=0).isoformat() + 'Z'

    instructions = (
        "Pague a referência numa caixa MB, homebanking ou app. "
        "Insira Entidade, Referência e Valor. "
        f"Validade: {validade_iso} UTC."
    )

    mb_data = {
        "success": True,
        "payment_method": "multibanco",
        "entidade": entidade,
        "referencia": referencia,
        "valor": f"{valor:.2f}",
        "validade": validade_iso,
        "instructions": instructions
    }

    ticket_id = str(uuid.uuid4())
    ticket = {
        "ticket_id": ticket_id,
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z',
        "payment": {
            "method": "multibanco",
            "entidade": entidade,
            "referencia": referencia,
            "valor": f"{valor:.2f}",
            "validade": validade_iso
        },
        "customer": {
            "nome": customer.get('nome'),
            "email": customer.get('email'),
            "telefone": telefone,
            "nif": nif
        },
        "basket": payload.get('basket') or payload.get('items') or {},
        "metadata": payload.get('metadata') or {}
    }
    _simulated_tickets[ticket_id] = ticket
    mb_data['ticket_id'] = ticket_id
    return jsonify(mb_data), 200

@paginas_bp.route('/api/tickets/create', methods=['POST'])
def api_tickets_create():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"success": False, "message": "JSON inválido"}), 400

    customer = payload.get('customer') or {}
    telefone = (customer.get('telefone') or customer.get('phone') or '').strip()
    nif = (customer.get('nif') or '').strip()

    if not telefone:
        return jsonify({"success": False, "message": "Telefone é obrigatório para criar ticket"}), 400
    if not _validate_phone(telefone):
        return jsonify({"success": False, "message": "Telefone inválido"}), 400

    if not nif:
        return jsonify({"success": False, "message": "NIF é obrigatório para criar ticket"}), 400
    if not _validate_nif(nif):
        return jsonify({"success": False, "message": "NIF inválido (9 dígitos)"}), 400

    ticket_id = str(uuid.uuid4())
    ticket = {
        "ticket_id": ticket_id,
        "created_at": datetime.datetime.utcnow().isoformat() + 'Z',
        "payload": payload
    }
    _simulated_tickets[ticket_id] = ticket
    return jsonify({"success": True, "ticket_id": ticket_id}), 201

@paginas_bp.route('/detalhes/<int:id>')
def detalhes(id):
    # procura templates/paginas/detalhes_<id>.html
    template_name = f'paginas/detalhes_{id}.html'
    try:
        return render_template(template_name)
    except TemplateNotFound:
        abort(404)