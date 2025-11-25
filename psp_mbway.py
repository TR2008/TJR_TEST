import os
import requests
from flask import Blueprint, request, jsonify, current_app

mbway_bp = Blueprint('mbway', __name__)
PSP_MBWAY_API = os.environ.get("PSP_MBWAY_API", "https://api-exemplo-psp.pt/mbway")
PSP_MBWAY_KEY = os.environ.get("PSP_MBWAY_KEY", "xxxx")

def start_mbway_payment(order_id, amount, phone, callback_url):
    payload = {
        "order_id": str(order_id),
        "amount": f"{amount:.2f}",
        "phone": phone,
        "callback_url": callback_url
    }
    headers = {"Authorization": f"Bearer {PSP_MBWAY_KEY}", "Content-Type": "application/json"}
    resp = requests.post(PSP_MBWAY_API + "/payments", json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()  # exemplo: {"payment_id":"abc123","status":"PENDING","deep_link": "..."}

@mbway_bp.route("/psp/mbway/start", methods=["POST"])
def mbway_start():
    data = request.get_json() or {}
    order_id = data.get("order_id")
    amount = float(data.get("amount", 0))
    phone = data.get("phone")
    if not order_id or amount <= 0 or not phone:
        return jsonify({"success": False, "message": "order_id, amount e phone obrigatórios"}), 400

    callback_url = data.get("callback_url") or (request.url_root.rstrip("/") + "/psp/mbway/ipn")
    try:
        resp = start_mbway_payment(order_id, amount, phone, callback_url)
        # Salve payment_id/status na DB e retorne link/info ao cliente
        return jsonify({"success": True, "mbway": resp}), 201
    except Exception as e:
        current_app.logger.exception("Erro MB WAY: %s", e)
        return jsonify({"success": False, "message": "Erro RPC PSP"}), 500

@mbway_bp.route("/psp/mbway/ipn", methods=["POST"])
def mbway_ipn():
    data = request.get_json() or {}
    # Campos típicos: payment_id, order_id, status ('CONFIRMED'|'FAILED'), amount
    payment_id = data.get("payment_id")
    status = data.get("status")
    order_id = data.get("order_id")
    # Validar origem, actualizar DB e faturar conforme status
    if status == "CONFIRMED":
        current_app.logger.info("MB WAY confirmado: %s -> order %s", payment_id, order_id)
        # marcar encomenda como paga
    else:
        current_app.logger.info("MB WAY falhado/other: %s", payment_id)
    return jsonify({"received": True})