import sqlalchemy.exc
from flask import Blueprint, request, redirect, url_for, flash
from .models import Usuario, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user
import bcrypt

auth = Blueprint('auth', __name__)


@auth.route('/cadastrar', methods=['post', ])
def cadastrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha1 = request.form.get('senha')
    senha2 = request.form.get('senha2')

    senha_sao_iguais = senha1 == senha2

    if not senha_sao_iguais:
        flash('Senhas não são iguais', category="error")
        return redirect(url_for('views.cadastro'))
    elif len(senha1) < 3:
        flash('Senha muito curta', category="error")
        return redirect(url_for('views.cadastro'))
    else:
        try:
            salt = bcrypt.gensalt()
            senha_cripto = bcrypt.hashpw(senha1.encode('utf-8'), salt)
            novo_usuario = Usuario(nome=nome, email=email, senha=senha_cripto, role=2)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso!', category="sucess")
        except sqlalchemy.exc.IntegrityError:
            flash('E-mail já registrado', category='error')
            return redirect(url_for('views.cadastro'))
        return redirect(url_for('views.home'))


@auth.route('/login-confirm', methods=['post', ])
def login_confirm():
    email_net = request.form.get('email')
    senha_net = request.form.get('senha')

    usuario = Usuario.query.filter_by(email=email_net).first()

    if usuario:
        if bcrypt.checkpw(senha_net.encode('utf-8'), usuario.senha.encode('utf-8')):
            flash('Logado com sucesso!', category='sucess')
            login_user(usuario, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Senha digitada inválida!', category='error')
            return redirect(url_for('views.login'))
    else:
        flash('Usuário não encontrado!', category='error')
        return redirect(url_for('views.login'))


@auth.route('/logout')
@login_required
def logout():
    flash('Deslogado com sucesso!', category='sucess')
    logout_user()
    return redirect(url_for('views.home'))