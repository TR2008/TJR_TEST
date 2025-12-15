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
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data
        utilizador = Utilizador.query.filter_by(email=email).first()
        # usar o nome real do método do seu modelo
        if utilizador and utilizador.check_password(senha):
            session['utilizador_id'] = utilizador.id
            return redirect(url_for('paginas.dashboard'))
        else:
            erro = "Email ou password incorretos."
            flash(erro, "danger")
            return render_template('auth/login.html', form=form, erro=erro)
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('utilizador_id', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/criar_utilizador', methods=['GET', 'POST'])
def criar_utilizador():
    form = RegistrationForm()
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data

        if Utilizador.query.filter_by(email=email).first():
            flash("Email já está registado.", "danger")
            return render_template('criar_utilizador.html', form=form)

        novo = Utilizador(nome=nome, email=email)
        novo.set_password(senha)   # usar o nome real do método do seu modelo
        db.session.add(novo)
        db.session.commit()

        flash("Conta criada com sucesso. Pode iniciar sessão.", "success")
        return redirect(url_for('auth.login'))

    return render_template('criar_utilizador.html', form=form)

# rota para inserir cliente (antes tinha duplicação). Ajuste a action/template conforme o seu projeto.
@auth_bp.route('/inserir_cliente', methods=['GET', 'POST'])
def inserir_cliente():
    form = RegisterForm()
    if form.validate_on_submit():
        # exemplo de criação de Cliente (importe/ajuste o modelo Cliente conforme o seu ficheiro models/__init__.py)
        from models import Cliente  # import tardio do modelo cliente se preferir
        if Cliente.query.filter_by(email=form.email.data).first():
            flash("Email do cliente já existe.", "danger")
            return render_template('login.html', reg_form=form, form=None)

        cliente = Cliente(
            nome=form.nome.data,
            morada=form.morada.data,
            localidade=form.localidade.data,
            codigo_postal=form.codigo_postal.data,
            concelho1=form.concelho1.data,
            concelho2=form.concelho2.data,
            nif=form.nif.data,
            email=form.email.data
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente inserido com sucesso.", "success")
        return redirect(url_for('auth.login'))

    return render_template('login.html', reg_form=form, form=None)

# manter alias se necessário
@auth_bp.route('/register', methods=['GET', 'POST'])
def register_alias():
    return redirect(url_for('auth.inserir_cliente'))