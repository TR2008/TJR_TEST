from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models import Utilizador, db
from forms import LoginForm, RegistrationForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if 'utilizador_id' in session:
        return redirect(url_for('paginas.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mensagem = None
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data
        utilizador = Utilizador.query.filter_by(email=email).first()
        # usar o nome real do método do seu modelo
        if utilizador and utilizador.check_password(senha):
            session['utilizador_id'] = utilizador.id
            return redirect(url_for('paginas.dashboard'))
        else:
            mensagem = "Email ou password incorretos."
            flash(mensagem, "danger")
            return render_template('login.html', form=form, mensagem=mensagem)
    return render_template('login.html', form=form, mensagem=mensagem)

@auth_bp.route('/logout')
def logout():
    session.pop('utilizador_id', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/criar_utilizador', methods=['GET', 'POST'])
def criar_utilizador():
    form = RegistrationForm()
    mensagem = None
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data

        if Utilizador.query.filter_by(email=email).first():
            mensagem = "Email já está registado."
            flash(mensagem, "danger")
            return render_template('criar_utilizador.html', form=form, mensagem=mensagem)

        novo = Utilizador(nome=nome, email=email)
        novo.set_password(senha)   # usar o nome real do método do seu modelo
        db.session.add(novo)
        db.session.commit()

        mensagem = "Conta criada com sucesso. Pode iniciar sessão."
        flash(mensagem, "success")
        return redirect(url_for('auth.login'))

    return render_template('criar_utilizador.html', form=form, mensagem=mensagem)

# rota para inserir cliente (antes tinha duplicação). Ajuste a action/template conforme o seu projeto.
@auth_bp.route('/inserir_cliente', methods=['GET', 'POST'])
def inserir_cliente():
    reg_form = RegisterForm()
    form = LoginForm()
    mensagem = None
    if reg_form.validate_on_submit():
        # exemplo de criação de Cliente (importe/ajuste o modelo Cliente conforme o seu ficheiro models/__init__.py)
        from models import Cliente  # import tardio do modelo cliente se preferir
        if Cliente.query.filter_by(email=reg_form.email.data).first():
            mensagem = "Email do cliente já existe."
            flash(mensagem, "danger")
            return render_template('login.html', reg_form=reg_form, form=form, mensagem=mensagem)

        cliente = Cliente(
            nome=reg_form.nome.data,
            morada=reg_form.morada.data,
            localidade=reg_form.localidade.data,
            codigo_postal=reg_form.codigo_postal.data,
            concelho1=reg_form.concelho1.data,
            concelho2=reg_form.concelho2.data,
            nif=reg_form.nif.data,
            email=reg_form.email.data
        )
        db.session.add(cliente)
        db.session.commit()
        mensagem = "Cliente inserido com sucesso."
        flash(mensagem, "success")
        return redirect(url_for('auth.login'))

    return render_template('login.html', reg_form=reg_form, form=form, mensagem=mensagem)

# rota register (deve ir para inserir_cliente)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return inserir_cliente()

# manter alias se necessário
@auth_bp.route('/register_alias', methods=['GET', 'POST'])
def register_alias():
    return redirect(url_for('auth.inserir_cliente'))