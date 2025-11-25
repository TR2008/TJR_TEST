// Cliente simples para iniciar pagamentos PayPal, MB WAY e wrapper (usar com o modal já existente)
async function startPayPalPayment(amount, items, customer) {
    try {
        const resp = await fetch('/api/payment/paypal/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                amount: Number(amount).toFixed(2),
                currency: 'EUR',
                description: 'Encomenda TJR',
                items: items,
                customer: customer,
                return_url: window.location.origin + '/paypal/return',
                cancel_url: window.location.origin + '/paypal/cancel'
            })
        });
        if (!resp.ok) {
            const txt = await resp.text();
            throw new Error('Erro servidor PayPal: ' + txt);
        }
        const data = await resp.json();
        if (data.success && data.approve_url) {
            // redirecionar para PayPal para aprovação
            window.location.href = data.approve_url;
        } else {
            alert('Não foi possível iniciar o pagamento PayPal.');
            console.error(data);
        }
    } catch (e) {
        console.error('Erro startPayPalPayment', e);
        alert('Erro ao iniciar PayPal: ' + (e.message || e));
    }
}

async function startMbwayPayment(amount, phone, items, customer) {
    try {
        const resp = await fetch('/api/payment/mbway', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                amount: Number(amount).toFixed(2),
                phone: phone,
                items: items,
                customer: customer
            })
        });
        if (!resp.ok) {
            const txt = await resp.text();
            throw new Error('Erro servidor MB WAY: ' + txt);
        }
        const data = await resp.json();
        if (data.success && data.mbway) {
            // Mostrar resultado no modal (usa #mb-result do produtos.html)
            const mbEl = document.getElementById('mb-result');
            mbEl.style.display = 'block';
            const info = data.mbway;
            mbEl.innerHTML = `<strong>MB WAY iniciado</strong>
                <div>ID: <strong>${escapeHtml(info.payment_id || info.id || '')}</strong></div>
                <div>Status: <strong>${escapeHtml(info.status || '')}</strong></div>
                <div style="margin-top:6px;" class="muted">${escapeHtml(info.instructions || info.message || '')}</div>`;
            return data;
        } else {
            alert('Não foi possível iniciar MB WAY.');
            console.error(data);
        }
    } catch (e) {
        console.error('Erro startMbwayPayment', e);
        alert('Erro ao iniciar MB WAY: ' + (e.message || e));
    }
}

// Função utilitária escape usada no template (copiar se não exisitr)
function escapeHtml(unsafe) {
    if (!unsafe && unsafe !== 0) return '';
    return String(unsafe)
        .replaceAll('&','&amp;')
        .replaceAll('<','&lt;')
        .replaceAll('>','&gt;')
        .replaceAll('"','&quot;')
        .replaceAll("'",'&#039;');
}