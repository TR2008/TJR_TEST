from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    senha2 = PasswordField('Confirmar Senha',
                           validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir')])
    submit = SubmitField('Cadastrar')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Enviar')


class ResetPasswordForm(FlaskForm):
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    senha2 = PasswordField('Confirmar Senha',
                           validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir')])
    submit = SubmitField('Redefinir Senha')


class RegisterForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=120)])
    morada = StringField('Morada', validators=[Optional(), Length(max=200)])
    localidade = StringField('Localidade', validators=[Optional(), Length(max=100)])
    codigo_postal = StringField('Código Postal', validators=[Optional(), Length(max=20)])
    concelho1 = StringField('Concelho 1', validators=[Optional(), Length(max=100)])
    concelho2 = StringField('Concelho 2', validators=[Optional(), Length(max=100)])
    nif = StringField('NIF', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    senha2 = PasswordField('Confirmar Senha',
                           validators=[DataRequired(), EqualTo('senha', message='As senhas devem coincidir')])
    submit = SubmitField('Inserir Cliente')
