from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Usuario, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user

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
        novo_usuario = Usuario(nome=nome, email=email, senha=generate_password_hash(senha1, 'sha256'))
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Conta criada com sucesso!', category="sucess")
        return redirect(url_for('views.home'))


@auth.route('/login-confirm', methods=['post', ])
def login_confirm():
    email_net = request.form.get('email')
    senha_net = request.form.get('senha')

    usuario = Usuario.query.filter_by(email=email_net).first()

    if usuario:
        if check_password_hash(usuario.senha, senha_net):
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