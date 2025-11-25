
from flask import Blueprint, request, jsonify, current_app
from models import db, Cliente, Encomenda  # adapta aos teus modelos reais
from datetime import datetime
import random
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
import tempfile

# Opcional: usar weasyprint para gerar PDF a partir de HTML
# pip install weasyprint
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

checkout_bp = Blueprint('checkout', __name__)

def gerar_ticket_5_digitos():
    return f"{random.randint(10000, 99999)}"

def gerar_html_fatura(cliente, encomenda, empresa_info):
    # Gera um HTML simples para transformar em PDF (ajusta layout conforme necessário)
    items_html = ""
    basket = encomenda.get('basket', {}) if isinstance(encomenda, dict) else {}
    # Se encomenda.items for uma string JSON, já deve estar normalizada no backend. Aqui damos fallback.
    for pid, it in (basket.items() if isinstance(basket, dict) else []):
        name = it.get('name') if isinstance(it, dict) else str(pid)
        qty = it.get('quantity', 1) if isinstance(it, dict) else 1
        price = float(it.get('price', 0)) if isinstance(it, dict) else 0
        line_total = qty * price
        items_html += f"<tr><td>{name}</td><td style='text-align:center'>{qty}</td><td style='text-align:right'>{price:.2f} €</td><td style='text-align:right'>{line_total:.2f} €</td></tr>"

    total = float(encomenda.get('summary', {}).get('total', 0)) if isinstance(encomenda, dict) else 0

    html = f"""
    <html>
    <head>
      <meta charset="utf-8"/>
      <style>
        body {{ font-family: Arial, sans-serif; color:#111; }}
        .header {{ display:flex; justify-content:space-between; align-items:center; }}
        .empresa {{ font-weight:700; font-size:18px; }}
        .small {{ font-size:12px; color:#444; }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th, td {{ padding:8px; border-bottom:1px solid #e6e6e6; }}
        th {{ text-align:left; background:#f7f7f7; }}
        .total-row td {{ font-weight:800; }}
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <div class="empresa">{empresa_info['nome']}</div>
          <div class="small">{empresa_info['morada']}</div>
          <div class="small">NIF: {empresa_info['nif']}</div>
        </div>
        <div style="text-align:right">
          <div>Data: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}</div>
          <div>Ticket: {encomenda.get('ticket')}</div>
          <div>Encomenda ID: {encomenda.get('order_id', '')}</div>
        </div>
      </div>

      <h3>Fatura / Recibo</h3>
      <div>
        <strong>Cliente:</strong> {cliente.get('nome')}<br/>
        <strong>Email:</strong> {cliente.get('email')}<br/>
        <strong>NIF:</strong> {cliente.get('nif')}<br/>
        <strong>Morada:</strong> {cliente.get('morada')} - {cliente.get('localidade')} / {cliente.get('concelho')}<br/>
        <strong>Código Postal:</strong> {cliente.get('codigo_postal')}
      </div>

      <table>
        <thead>
          <tr><th>Produto / Serviço</th><th style='text-align:center'>Qtd</th><th style='text-align:right'>Preço</th><th style='text-align:right'>Total</th></tr>
        </thead>
        <tbody>
          {items_html}
          <tr class="total-row"><td></td><td></td><td style="text-align:right">Total</td><td style="text-align:right">{total:.2f} €</td></tr>
        </tbody>
      </table>

      <p class="small">Documento automático gerado por TJR Unipessoal — Para qualquer questão contacte-nos.</p>
    </body>
    </html>
    """
    return html

def enviar_email_com_anexo(smtp_cfg, remetente_nome, remetente_email, destinatario_email, assunto, corpo_texto, attachment_path, attachment_filename):
    """
    Envia email usando smtplib. smtp_cfg é dict com host, port, username, password, use_tls (bool).
    """
    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = formataddr((remetente_nome, remetente_email))
    msg['To'] = destinatario_email
    msg.set_content(corpo_texto)

    # carrega anexo
    if attachment_path and Path(attachment_path).exists():
        with open(attachment_path, 'rb') as f:
            data = f.read()
        maintype = 'application'
        subtype = 'pdf'
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=attachment_filename)

    # enviar via SMTP
    host = smtp_cfg.get('host')
    port = int(smtp_cfg.get('port', 587))
    user = smtp_cfg.get('username')
    pwd = smtp_cfg.get('password')
    use_tls = smtp_cfg.get('use_tls', True)

    if use_tls:
        server = smtplib.SMTP(host, port, timeout=20)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(host, port, timeout=20)

    if user and pwd:
        server.login(user, pwd)
    server.send_message(msg)
    server.quit()

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

    try:
        # Procurar cliente por email (evita duplicados)
        existing = None
        try:
            existing = Cliente.query.filter_by(email=customer.get('email')).first()
        except Exception:
            existing = None

        if existing:
            cliente_obj = existing
            # atualizar campos relevantes
            cliente_obj.nome = customer.get('nome')
            cliente_obj.nif = customer.get('nif')
            cliente_obj.morada = customer.get('morada')
            cliente_obj.localidade = customer.get('localidade')
            cliente_obj.concelho = customer.get('concelho')
            cliente_obj.codigo_postal = customer.get('codigo_postal')
        else:
            cliente_obj = Cliente(
                nome=customer.get('nome'),
                email=customer.get('email'),
                nif=customer.get('nif'),
                morada=customer.get('morada'),
                localidade=customer.get('localidade'),
                concelho=customer.get('concelho'),
                codigo_postal=customer.get('codigo_postal'),
                criado_em=datetime.utcnow()
            )
            db.session.add(cliente_obj)
            db.session.flush()  # para obter id

        # criar encomenda
        encomenda_obj = Encomenda(
            cliente_id=cliente_obj.id,
            items=str(basket),   # ideal: serializar apropriadamente; adaptar ao teu modelo
            total=summary.get('total', 0),
            estado='Pendente',
            metodo_pagamento=payment_method,
            criado_em=datetime.utcnow()
        )
        db.session.add(encomenda_obj)
        db.session.flush()

        # gerar ticket e guardar se campo existir
        ticket = gerar_ticket_5_digitos()
        if hasattr(encomenda_obj, 'ticket'):
            encomenda_obj.ticket = ticket

        db.session.commit()

        # montar objecto que será usado no PDF
        encomenda_summary = {
            'order_id': encomenda_obj.id,
            'ticket': ticket,
            'basket': basket,
            'summary': summary
        }

        # empresa info fixo (conforme pedido)
        empresa_info = {
            'nome': 'TJR Unipessoal',
            'nif': '230810551',
            'morada': 'Rua Antonio Nobre nº4 4 A2745-839 Queluz'
        }

        # gerar PDF (se weasyprint disponível)
        pdf_path = None
        try:
            html = gerar_html_fatura(customer, encomenda_summary, empresa_info)
            if WEASYPRINT_AVAILABLE:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpf:
                    HTML(string=html).write_pdf(tmpf.name)
                    pdf_path = tmpf.name
            else:
                # Se WeasyPrint não estiver disponível, podemos gravar o HTML como fallback
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmpf:
                    tmpf.write(html)
                    pdf_path = tmpf.name  # não é PDF, mas será anexado como HTML se necessário
        except Exception as e:
            # Falha na geração do PDF não impede envio do email, prosseguimos sem anexo
            current_app.logger.exception("Erro a gerar PDF de fatura: %s", e)
            pdf_path = None

        # configuração SMTP via variáveis de ambiente (define no teu ambiente de execução)
        smtp_cfg = {
            'host': os.environ.get('SMTP_HOST', 'smtp.example.com'),
            'port': int(os.environ.get('SMTP_PORT', 587)),
            'username': os.environ.get('SMTP_USER', ''),
            'password': os.environ.get('SMTP_PASS', ''),
            'use_tls': os.environ.get('SMTP_TLS', '1') != '0'
        }
        remetente_nome = os.environ.get('EMAIL_FROM_NAME', 'TJR Unipessoal')
        remetente_email = os.environ.get('EMAIL_FROM', 'noreply@tjrunipessoal.pt')

        # preparar email
        assunto = f"Confirmação de Encomenda / Ticket {ticket}"
        corpo = f"Olá {customer.get('nome')},\n\nObrigado pela sua encomenda. O seu ticket é {ticket}.\nEncomenda ID: {encomenda_obj.id}\nTotal estimado: {summary.get('total', 0)} €\n\nEm anexo encontra a fatura/documento.\n\nCumprimentos,\n{empresa_info['nome']}"

        # enviar email (tenta, mas não falhará a resposta da API)
        try:
            if pdf_path:
                enviar_email_com_anexo(smtp_cfg, remetente_nome, remetente_email, customer.get('email'), assunto, corpo, pdf_path, f'fatura_{encomenda_obj.id}.pdf')
            else:
                # enviar sem anexo
                enviar_email_com_anexo(smtp_cfg, remetente_nome, remetente_email, customer.get('email'), assunto, corpo, None, None)
        except Exception as e:
            current_app.logger.exception("Erro ao enviar email de confirmação: %s", e)
            # não falhar a API por causa do email; retorna aviso ao cliente
            return jsonify({
                'success': True,
                'message': 'Encomenda criada, mas ocorreu um erro ao enviar o email (ver logs).',
                'order_id': encomenda_obj.id,
                'ticket': ticket
            }), 201

        # resposta final de sucesso
        return jsonify({
            'success': True,
            'message': 'Encomenda criada e email enviado com a fatura.',
            'order_id': encomenda_obj.id,
            'ticket': ticket
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro interno checkout: %s", e)
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500