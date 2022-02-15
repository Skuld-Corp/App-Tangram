import sqlalchemy.exc
import datetime
import bcrypt
import yagmail
from flask import Blueprint, request, redirect, url_for, flash
from .models import Usuario, db, TangramCoin, SenhaReset
from flask_login import login_required, login_user, logout_user, current_user
from .help_functions import tem_saldo_suficiente, gerar_key, email_user, email_passw, url_do_site


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
                        db.session.add(novo_professor)
                        db.session.commit()
                        flash('Professor cadastrado com sucesso!', category="success")
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


@auth.route('/resetar_senha', methods=['POST',])
def resetar_senha():
    email = request.form.get('email')
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario:
        ja_tem_senha_reset = SenhaReset.query.filter_by(user_id = usuario.id).first()
        if ja_tem_senha_reset:
            if ja_tem_senha_reset.has_activated is False:
                ja_tem_senha_reset.datetime = datetime.datetime.now()
                chave = ja_tem_senha_reset.reset_key
            else:
                chave = gerar_key()
                ja_tem_senha_reset.reset_key = chave
                ja_tem_senha_reset.datetime = datetime.datetime.now()
                ja_tem_senha_reset.has_activated = False
        else:
            chave = gerar_key()
            user_reset = SenhaReset(reset_key=chave, user_id=usuario.id)
            db.session.add(user_reset)
        db.session.commit()
        yag = yagmail.SMTP(email_user(), email_passw())
        url_site = url_do_site()
        contents = ['Por favor acesse essa url para trocar a senha:',
                    url_site + url_for("views.nova_senha_get", id=(str(chave)))]
        email_cadastrado = request.form.get("email")
        yag.send(email_cadastrado, 'Reset your password', contents)
        flash(usuario.nome + ", Confira seu Email para trocar de senha, verifique o spam também! Link expira em 45 mins!", category='success')
        return redirect(url_for("views.home"))
    else:
        flash("Email não encontrado!", category='error')
        return redirect(url_for('views.reset_senha'))


@auth.route("/troca-senha/<id>", methods=['POST',])
def nova_senha_post(id):
    if request.form["senha1"] != request.form["senha2"]:
        flash("As senhas estão diferentes", category="error")
        return redirect(url_for("views.nova_senha_get", id=id))
    if len(request.form["senha1"]) < 3:
        flash("Senha muito curta!", category="error")
        return redirect(url_for("views.nova_senha_get", id=id))
    usuario_reset = SenhaReset.query.filter_by(reset_key=id).one()
    try:
        salt = bcrypt.gensalt()
        senha1 = request.form.get("senha1")
        senha_cripto = bcrypt.hashpw(senha1.encode('utf-8'), salt)
        usuario = Usuario.query.filter_by(id=usuario_reset.user_id).update({'senha': senha_cripto})
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        flash("Aconteceu algum erro!", category="error")
        db.session.rollback()
        return redirect(url_for("views.home"))
    usuario_reset.has_activated = True
    db.session.commit()
    flash("Senha trocado com sucesso!", category="success")
    return redirect(url_for("views.home"))
