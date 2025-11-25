
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
PAYPAL_CLIENT = os.environ.get("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET")
PAYPAL_API = "https://api-m.sandbox.paypal.com"  # sandbox -> trocar para production

def get_access_token():
    resp = requests.post(f"{PAYPAL_API}/v1/oauth2/token",
                         auth=(PAYPAL_CLIENT, PAYPAL_SECRET),
                         data={"grant_type": "client_credentials"})
    resp.raise_for_status()
    return resp.json()["access_token"]

@app.route("/paypal/create-order", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": data.get("currency", "EUR"),
                    "value": f"{data.get('amount', '0.00')}"
                },
                "description": data.get("description", "Encomenda TJR")
            }
        ],
        "application_context": {
            "return_url": data.get("return_url"),
            "cancel_url": data.get("cancel_url")
        }
    }
    resp = requests.post(f"{PAYPAL_API}/v2/checkout/orders", json=order_payload, headers=headers)
    resp.raise_for_status()
    return jsonify(resp.json())

@app.route("/paypal/capture/<order_id>", methods=["POST"])
def capture_order(order_id):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    resp = requests.post(f"{PAYPAL_API}/v2/checkout/orders/{order_id}/capture", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Atualizar DB: registar encomenda como paga, enviar email/fatura, etc.
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5001, debug=True)