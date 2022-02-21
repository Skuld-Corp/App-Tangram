import sqlalchemy.exc
import datetime
import bcrypt
import yagmail
from flask import Blueprint, request, redirect, url_for, flash
from .models import Usuario, db, TangramCoin, SenhaReset, PerguntasQuiz, PerguntasRespondidas, PerguntasDesempenho
from flask_login import login_required, login_user, logout_user, current_user
from .help_functions import gerar_key, email_user, email_passw, \
    url_do_site, atualizar_perfil_func, eh_menor_que_essa_quantidade_de_caracters, atualizar_pergunta_func


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
        try:
            yag.send(email_cadastrado, 'Reset your password', contents)
            flash(usuario.nome + ", Confira seu Email para trocar de senha, verifique o spam também! Link expira em 45 mins!", category='success')
            return redirect(url_for("views.home"))
        except:
            flash(usuario.nome + ", Ocorreu algum erro ao enviar o Email, verifique se o seu Email é válido!", category='error')
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
        Usuario.query.filter_by(id=usuario_reset.user_id).update({'senha': senha_cripto})
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        flash("Aconteceu algum erro!", category="error")
        db.session.rollback()
        return redirect(url_for("views.home"))
    usuario_reset.has_activated = True
    db.session.commit()
    flash("Senha trocado com sucesso!", category="success")
    return redirect(url_for("views.home"))


@auth.route('/atualizar-perfil', methods=['POST',])
def atualizar_perfil():
    if request.form.get('atualiza') == 'Atualizar Perfil':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        try:
            if atualizar_perfil_func(nome, email, senha):
                db.session.commit()
                flash("Perfil atualizado com sucesso!", category="success")
            else:
                flash("Nada foi atualizado", category="warming")
        except sqlalchemy.exc.IntegrityError:
            flash("Email já em uso", category="error")
            db.session.rollback()
        return redirect(url_for('views.perfil'))
    if request.form.get('deleta') == 'Deletar a conta':
        try:
            user = db.session.query(Usuario).filter(Usuario.id == current_user.id).first()
            db.session.delete(user)
            db.session.commit()
            flash("Conta deletado com sucesso!", category="success")
            return redirect(url_for('views.login'))
        except sqlalchemy.exc.IntegrityError:
            flash("Aconteceu algum erro", category="error")
            db.session.rollback()
        return redirect(url_for('views.perfil'))


@auth.route('/nova_pergunta_create', methods=['POST',])
def nova_pergunta():
    titulo = request.form.get('titulo')
    pergunta = request.form.get('pergunta')
    resposta_1 = request.form.get('resposta_1')
    resposta_2 = request.form.get('resposta_2')
    resposta_3 = request.form.get('resposta_3')
    resposta_4 = request.form.get('resposta_4')
    resposta_certa = request.form.get('resposta_certa')
    questao_dificuldade = request.form.get('questao_dificuldade')
    if not eh_menor_que_essa_quantidade_de_caracters(titulo, 79):
        flash("Seu título é muito comprido, por favor o diminua", category='warming')
        return redirect(url_for('views.nova_pergunta'))
    else:
        if resposta_certa == 'Selecione a resposta correta':
            flash("Você não selecionou a resposta para a pergunta!", category='warming')
            return redirect(url_for('views.nova_pergunta'))
        else:

            try:
                novo_pergunta = PerguntasQuiz(professor_id=current_user.id, pergunta_titulo=titulo,
                                              pergunta=pergunta, resp_1=resposta_1,
                                              resp_2=resposta_2, resp_3=resposta_3,
                                              resp_4=resposta_4, resposta_certa=int(resposta_certa),
                                              questao_dificuldade=questao_dificuldade)

                db.session.add(novo_pergunta)
                db.session.commit()
                flash("Pergunta Registrada com sucesso!", category='success')
            except:
                flash("Ops, ocorreu algum erro!", category="error")
            return redirect(url_for('views.home'))


@auth.route('/resposta_verificacao', methods=['POST',])
def verificar_resposta():
    resposta_escolhida = int(request.form.get('resposta'))
    id_pergunta = request.form.get('pergunta_id')
    pergunta = PerguntasQuiz.query.filter_by(id=id_pergunta).first()
    acertou = resposta_escolhida == pergunta.resposta_certa
    if acertou:
        flash("Voceu acertou! Parabéns!", category="success")
        pergunta_respondida = PerguntasRespondidas(aluno_id=current_user.id, pergunta_id=id_pergunta)
        carteira = TangramCoin.query.filter_by(player_id=current_user.id).first()
        desempenho = PerguntasDesempenho.query.filter_by(aluno_id=current_user.id).first()
        desempenho.total_de_perguntas_respondidas += 1
        desempenho.total_de_perguntas_acertadas += 1
        saldo_ganho_por_acertar = 0
        if pergunta.questao_dificuldade == "facil":
            saldo_ganho_por_acertar = 10
        elif pergunta.questao_dificuldade == "medio":
            saldo_ganho_por_acertar = 50
        elif pergunta.questao_dificuldade == "dificil":
            saldo_ganho_por_acertar = 100
        carteira.saldo = carteira.saldo + saldo_ganho_por_acertar
        db.session.add(pergunta_respondida)
        db.session.commit()
    else:
        flash("Infelizmente, você errou! Tente novamente!", category="error")
        desempenho = PerguntasDesempenho.query.filter_by(aluno_id=current_user.id).first()
        desempenho.total_de_perguntas_respondidas += 1
        db.session.commit()
    return redirect(url_for('views.responder_quiz'))


@auth.route('atualiza_pergunta', methods=['POST',])
def atualizar_pergunta():
    if request.form.get('deleta') == 'Deletar':
        try:
            pergunta_id = request.form.get("pergunta_id")
            pergunta = db.session.query(PerguntasQuiz).filter(PerguntasQuiz.id == pergunta_id).first()
            db.session.delete(pergunta)
            db.session.commit()
            flash("Pergunta deletada com sucesso!", category="success")
            return redirect(url_for('views.perguntas_dash'))
        except sqlalchemy.exc.IntegrityError:
            flash("Aconteceu algum erro", category="error")
            db.session.rollback()
        return redirect(url_for('views.perfil'))
    elif request.form.get('info') == 'Editar':
        pergunta_id = request.form.get("pergunta_id")
        return redirect(url_for('views.editar_pergunta', id=pergunta_id))
    else:
        pergunta_id = request.form.get('pergunta_id')
        pergunta = db.session.query(PerguntasQuiz).filter(PerguntasQuiz.id == pergunta_id).first()
        titulo = request.form.get('titulo')
        pergunta_questao = request.form.get('pergunta')
        resposta_1 = request.form.get('resposta_1')
        resposta_2 = request.form.get('resposta_2')
        resposta_3 = request.form.get('resposta_3')
        resposta_4 = request.form.get('resposta_4')
        resposta_certa = request.form.get('resposta_certa')
        questao_dificuldade = request.form.get('questao_dificuldade')
        if not eh_menor_que_essa_quantidade_de_caracters(titulo, 79):
            flash("Seu título é muito comprido, por favor o diminua", category='warming')
            return redirect(url_for('views.editar_pergunta', id=pergunta_id))
        else:
            if resposta_certa == 'Selecione a resposta correta':
                flash("Você não selecionou a resposta para a pergunta!", category='warming')
                return redirect(url_for('views.editar_pergunta', id=pergunta_id))
            else:
                atualizar_pergunta_func(pergunta, titulo, pergunta_questao, resposta_1, resposta_2, resposta_3,
                                        resposta_4, resposta_certa, questao_dificuldade)
                db.session.commit()
                flash("Questão atualizada com sucesso", category="success")
                return redirect(url_for('views.editar_pergunta', id=pergunta_id))
