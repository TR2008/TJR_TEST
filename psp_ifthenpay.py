import os
import hmac
import hashlib
import requests
from flask import Blueprint, request, jsonify, current_app

psp_bp = Blueprint('psp', __name__)

# Config (defina nas variáveis de ambiente)
IFTHENPAY_API_URL = os.environ.get("IFTHENPAY_API_URL", "https://api-exemplo-psp.pt/multibanco")
IFTHENPAY_API_KEY = os.environ.get("IFTHENPAY_API_KEY", "xxxx")
IFTHENPAY_WEBHOOK_SECRET = os.environ.get("IFTHENPAY_WEBHOOK_SECRET", "secret")  # se PSP fornecer

def request_mb_reference(order_id, amount, callback_url, description=None):
    """
    Chama o endpoint do PSP para gerar Entidade/Referência.
    Substitua 'payload' e headers conforme doc do PSP.
    """
    payload = {
        "order_id": str(order_id),
        "amount": f"{amount:.2f}",
        "callback_url": callback_url,
        "description": description or f"Encomenda {order_id}"
    }
    headers = {
        "Authorization": f"Bearer {IFTHENPAY_API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(IFTHENPAY_API_URL + "/create_reference", json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()  # espera: {"entidade":"12345","referencia":"123 456 789","valor":"12.34","validade":"2025-11-25"}

@psp_bp.route("/psp/mb/create", methods=["POST"])
def create_mb_reference():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    amount = float(data.get("amount", 0))
    if not order_id or amount <= 0:
        return jsonify({"success": False, "message": "order_id e amount obrigatórios"}), 400

    # callback público que o PSP chamará quando houver confirmação
    callback_url = data.get("callback_url") or (request.url_root.rstrip("/") + "/psp/mb/ipn")

    try:
        resp = request_mb_reference(order_id, amount, callback_url, description=data.get("description"))
        # Salve entidade/referencia/validade na base de dados ligada à encomenda (p.ex. Encomenda.mb_entidade)
        # Exemplos de retorno para o cliente:
        return jsonify({"success": True, "mb_info": resp}), 201
    except Exception as e:
        current_app.logger.exception("Erro a criar referência MB: %s", e)
        return jsonify({"success": False, "message": "Erro RPC ao PSP"}), 500

def verify_psp_signature(payload_bytes, header_signature):
    """
    Se o PSP usar HMAC ou assinatura, valide aqui. Ajuste conforme doc.
    Exemplo HMAC-SHA256:
    """
    if not IFTHENPAY_WEBHOOK_SECRET:
        return True
    computed = hmac.new(IFTHENPAY_WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, header_signature or "")

@psp_bp.route("/psp/mb/ipn", methods=["POST"])
def mb_ipn():
    payload = request.get_data()
    headers = request.headers
    signature = headers.get("X-PSP-Signature")  # pode variar
    if not verify_psp_signature(payload, signature):
        return jsonify({"error": "invalid signature"}), 400

    data = request.get_json() or {}
    # Exemplos de campos: order_id, entidade, referencia, amount, status ('paid'|'expired')
    order_id = data.get("order_id")
    status = data.get("status")
    paid_amount = data.get("amount")

    # TODO: carregar encomenda da DB por order_id e verificar entidade/referencia coincidem
    # if not order or entidade/ref diferentes: log e retornar 400

    if status == "paid":
        # Atualizar encomenda para Pago; gravar recibo/fatura; enviar email
        # p.ex.: encomenda.estado = 'Pago'; db.session.commit()
        current_app.logger.info("Encomenda %s foi paga: %s", order_id, paid_amount)
    elif status == "expired":
        # Atualizar para expirado/cancelado
        current_app.logger.info("Encomenda %s expirou", order_id)

    # Retornar 200 OK para o PSP confirmar que recebeu
    return jsonify({"received": True})