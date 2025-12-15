# Instruções de Deploy para cPanel (Passenger)

Este documento descreve como fazer o deploy da aplicação Flask no cPanel com Passenger.

## Pré-requisitos

- Acesso ao cPanel do domínio hvacsolution81.com
- Python 3.9 ou superior disponível no cPanel
- Acesso SSH (opcional, mas recomendado)

## Passo 1: Preparar o ZIP da aplicação

1. Na sua máquina local, navegue até o diretório do projeto
2. Crie um arquivo ZIP com todos os ficheiros necessários:

```bash
zip -r app_deploy.zip \
    app.py \
    passenger_wsgi.py \
    config.py \
    forms.py \
    requirements.txt \
    models/ \
    routes/ \
    templates/ \
    static/ \
    -x "*.pyc" -x "__pycache__/*" -x "*.db" -x ".git/*"
```

**Nota:** NÃO incluir no ZIP:
- Ficheiros `.pyc` ou `__pycache__`
- Base de dados local (`.db`)
- Diretório `.git`
- Ambientes virtuais (`venv`, `env`)

## Passo 2: Upload para o cPanel

### Opção A: Via File Manager do cPanel

1. Aceda ao cPanel → File Manager
2. Navegue até `public_html/` (ou subdiretório desejado)
3. Faça upload do `app_deploy.zip`
4. Clique com botão direito no ficheiro ZIP → Extract
5. Remova o ficheiro ZIP após extração

### Opção B: Via SSH/SCP

```bash
scp app_deploy.zip usuario@hvacsolution81.com:~/public_html/
ssh usuario@hvacsolution81.com
cd ~/public_html
unzip app_deploy.zip
rm app_deploy.zip
```

## Passo 3: Configurar Python App no cPanel

1. No cPanel, vá para **Setup Python App**
2. Clique em **Create Application**
3. Configure:
   - **Python Version:** 3.9 ou superior
   - **Application Root:** `/home/usuario/public_html` (ajuste conforme necessário)
   - **Application URL:** `/` (ou subdomínio/subpath)
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`

4. Clique em **Create**

## Passo 4: Configurar Variáveis de Ambiente

Na secção **Environment Variables** da Python App:

1. Adicione as seguintes variáveis:

```
SECRET_KEY=<gere_uma_chave_secreta_forte_aqui>
DATABASE_URL=sqlite:////home/usuario/public_html/app.db
FLASK_ENV=production
```

**Para gerar uma SECRET_KEY segura:**
```python
import secrets
print(secrets.token_hex(32))
```

**Se usar MySQL no cPanel:**
```
DATABASE_URL=mysql+pymysql://usuario_db:senha@localhost/nome_db
```

## Passo 5: Instalar Dependências

1. Na interface **Setup Python App**, clique no botão **Run Pip Install**
2. Ou via terminal virtual env:

```bash
source /home/usuario/virtualenv/public_html/3.9/bin/activate
pip install -r requirements.txt
```

## Passo 6: Criar Tabelas da Base de Dados

Via SSH no ambiente virtual:

```bash
source /home/usuario/virtualenv/public_html/3.9/bin/activate
cd ~/public_html
python -c "from app import app; from models import db; app.app_context().push(); db.create_all(); print('Tabelas criadas!')"
```

## Passo 7: Reiniciar a Aplicação

No cPanel → Setup Python App → clique no botão **Restart** ou:

```bash
touch ~/public_html/passenger_wsgi.py
```

## Passo 8: Testar a Aplicação

1. Abra o browser e aceda a `https://hvacsolution81.com/`
2. Deve ver a mensagem: "Flask Application is running! Visit /login to access the application."
3. Teste as rotas principais:
   - `/login` - Página de login
   - `/criar_utilizador` - Criar novo utilizador
   - `/dashboard` - Dashboard (requer autenticação)

## Estrutura de Diretórios no Servidor

```
public_html/
├── app.py
├── passenger_wsgi.py
├── config.py
├── forms.py
├── requirements.txt
├── app.db (criado automaticamente)
├── models/
│   └── __init__.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── paginas.py
│   ├── produto.py
│   ├── cliente.py
│   └── basket.py
├── templates/
│   ├── auth/
│   ├── paginas/
│   └── ...
└── static/
    ├── css/
    ├── js/
    └── images/
```

## Troubleshooting

### Erro 500 Internal Server Error

1. Verifique os logs em cPanel → **Errors** (últimas 300 entradas)
2. Ou via SSH:
```bash
tail -f ~/logs/hvacsolution81.com-error_log
```

### ModuleNotFoundError

- Verifique se todas as dependências estão instaladas: `pip list`
- Reinstale requirements: `pip install -r requirements.txt --upgrade`

### Problemas de Permissões

```bash
chmod 755 ~/public_html
chmod 644 ~/public_html/*.py
chmod 755 ~/public_html/passenger_wsgi.py
```

### Base de Dados SQLite Locked

- Verifique permissões: `chmod 664 app.db`
- Considere usar MySQL para produção

## Actualizações Futuras

Para actualizar a aplicação:

1. Faça backup da base de dados atual:
```bash
cp app.db app.db.backup
```

2. Faça upload dos ficheiros alterados via File Manager ou SCP

3. Se houver novas dependências, actualize:
```bash
source /home/usuario/virtualenv/public_html/3.9/bin/activate
pip install -r requirements.txt
```

4. Reinicie a aplicação:
```bash
touch passenger_wsgi.py
```

## Segurança

⚠️ **IMPORTANTE:**

- **NUNCA** commite a SECRET_KEY no código
- Use variáveis de ambiente para dados sensíveis
- Mantenha `FLASK_ENV=production` em produção
- Configure HTTPS no cPanel (Let's Encrypt gratuito)
- Faça backups regulares da base de dados
- Mantenha as dependências atualizadas

## Suporte

Para problemas específicos do cPanel/Passenger:
- Documentação oficial: https://www.phusionpassenger.com/
- Suporte do hosting provider

Para problemas da aplicação Flask:
- Verifique os logs de erro
- Teste localmente primeiro antes de fazer deploy
