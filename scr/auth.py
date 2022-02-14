import sqlalchemy.exc
from flask import Blueprint, request, redirect, url_for, flash
from .models import Usuario, db, TangramCoin
from flask_login import login_required, login_user, logout_user, current_user
import bcrypt
from .help_functions import tem_saldo_suficiente

auth = Blueprint('auth', __name__)


@auth.route('/cadastrar', methods=['POST',])
def cadastrar():
    if request.method == "POST":
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
                if current_user.is_authenticated:
                    # cria professor se for admin
                    if current_user.has_role == 1:
                        novo_professor = Usuario(nome=nome, email=email, senha=senha_cripto, role=2)
                        flash('Professor cadastrado com sucesso!', category="success")
                        db.session.add(novo_professor)
                        db.session.commit()
                else:
                    # aluno default
                    novo_usuario = Usuario(nome=nome, email=email, senha=senha_cripto, role=3)
                    db.session.add(novo_usuario)
                    db.session.commit()
                    flash('Conta criada com sucesso!', category="success")
            except sqlalchemy.exc.IntegrityError:
                flash('E-mail já registrado', category='error')
                return redirect(url_for('views.cadastro'))
            return redirect(url_for('views.home'))


@auth.route('/login-confirm', methods=['POST', ])
def login_confirm():
    if request.method == "POST":
        email_net = request.form.get('email')
        senha_net = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email_net).first()

        if usuario:
            if bcrypt.checkpw(senha_net.encode('utf-8'), usuario.senha):
                flash('Logado com sucesso!', category='sucess')
                login_user(usuario, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Senha digitada inválida!', category='error')
                return redirect(url_for('views.login'))
        else:
            # verificação "atoa" para evitar > "ACCOUNT ENUMERATION VIA TIMING ATTACKS"
            senha_hash = "$2a$12$zlU2BApnYUfTsxOUgOQ8wuk.cFsFqFq2g.d/DC3X2N74TOa7yF27e"
            if bcrypt.checkpw(senha_net.encode('utf-8'), senha_hash.encode('utf-8')):
                pass
            flash('Usuário não encontrado!', category='error')
            return redirect(url_for('views.login'))


@auth.route('/logout')
@login_required
def logout():
    flash('Deslogado com sucesso!', category='sucess')
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/depositar', methods=['POST',])
@login_required
def deposita():
    if request.method == "POST":
        eh_aluno = current_user.role
        if eh_aluno:
            saldo_a_depositar = request.form.get('saldo_deposita')
            carteira_do_usuario = TangramCoin.query.filter_by(player_id=current_user.id).first()
            carteira_do_usuario.saldo += int(saldo_a_depositar)
            db.session.add(carteira_do_usuario)
            db.session.commit()
            flash("Saldo depositado com sucesso!", category='sucess')
            return redirect(url_for('views.home'))
        else:
            flash("Ops algo deu errado!", category='error')
            return redirect(url_for('views.home'))


@auth.route('/sacar', methods=['POST',])
@login_required
def sacar():
    if request.method == "POST":
        eh_aluno = current_user.role
        if eh_aluno:
            saldo_a_sacar = int(request.form.get('saldo_sacar'))
            carteira_do_usuario = TangramCoin.query.filter_by(player_id=current_user.id).first()
            if tem_saldo_suficiente(carteira_do_usuario.saldo, saldo_a_sacar):
                carteira_do_usuario.saldo -= saldo_a_sacar
                db.session.add(carteira_do_usuario)
                db.session.commit()
                flash("Saldo sacado com sucesso!", category='sucess')
            else:
                flash("Saldo Insuficiente", category='error')
            return redirect(url_for('views.home'))
        else:
            flash("Ops algo deu errado!", category='error')
            return redirect(url_for('views.home'))
