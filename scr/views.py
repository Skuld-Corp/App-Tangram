import pytz
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import SenhaReset, db, PerguntasQuiz, PerguntasRespondidas, PerguntasDesempenho
import datetime
from random import choice


views = Blueprint('views', __name__)


@views.route('/')
def home():
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        desempenho = PerguntasDesempenho.query.filter_by(aluno_id=current_user.id).first()
        return render_template('home.html', user=current_user, desempenho=desempenho)





@views.route('/login')
def login():
    if current_user.is_authenticated:
        flash('Você já esta logado!', category="sucess")
        return redirect(url_for('views.home'))
    else:
        return render_template('login.html', user=current_user)


@views.route('/reset-senha')
def reset_senha():
    if current_user.is_authenticated:
        flash('Você já esta logado!', category="sucess")
        return redirect(url_for('views.home'))
    else:
        return render_template('esqueceu_senha_solicitar.html')


@views.route('/troca-senha/<id>', methods=['GET',])
def nova_senha_get(id):
    chave = id
    senha_reset_chave = SenhaReset.query.filter_by(reset_key=id).one()
    if senha_reset_chave:
        aberto_em = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(minutes=45)
        gerou_em = senha_reset_chave.datetime
        gerou_em.replace(tzinfo=pytz.utc)
        if senha_reset_chave.has_activated is True:
            flash("Você ja usou esse link para trocar a senha. Por favor, gere um novo link", category="error")
            return redirect(url_for('views.reset_senha'))
        if gerou_em < aberto_em:
            flash("O seu link de trocar a senha expirou. Por favor, gere um novo link", category="error")
            return redirect(url_for('views.reset_senha'))
        return render_template("nova_senha.html", id=chave)
    else:
        flash("Não foi possível localizar esse endereço", category="error")
        return redirect(url_for("views.home"))


@views.route('/perfil')
def perfil():
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        return render_template('perfil.html', user=current_user)


@views.route('/nova-pergunta')
def nova_pergunta():
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        if current_user.has_role == 2:
            return render_template('criar_perguntas.html', user=current_user)
        else:
            flash("Você não tem permissão para fazer isso!", category="error")
            return redirect(url_for('views.home'))


@views.route("/quiz")
def responder_quiz():
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        if current_user.has_role == 3:
            perguntas_respondidas_ids = set()
            perguntas_lista_com_ids = set()
            perguntas = PerguntasQuiz.query.order_by(PerguntasQuiz.id).all()
            perguntas_respondida_pelo_usuario = PerguntasRespondidas.query.filter_by(aluno_id=current_user.id).all()
            total_de_perguntas_respondidas = len(perguntas_respondida_pelo_usuario)
            total_de_perguntas = len(perguntas)
            for i in range(total_de_perguntas_respondidas):
                perguntas_respondidas_ids.add(perguntas_respondida_pelo_usuario[i].pergunta_id)
            for i in range(total_de_perguntas):
                perguntas_lista_com_ids.add(perguntas[i].id)
            del total_de_perguntas_respondidas, total_de_perguntas, perguntas, perguntas_respondida_pelo_usuario
            perguntas_nao_respondidas = perguntas_lista_com_ids - perguntas_respondidas_ids
            ha_perguntas_para_responder = len(perguntas_nao_respondidas)
            if ha_perguntas_para_responder == 0:
                flash("Parabéns, você já respondeu todas as nossas perguntas!", category="success")
                return redirect(url_for('views.home'))
            pergunta_escolhida_id = choice(tuple(perguntas_nao_respondidas))
            pergunta_escolhida = PerguntasQuiz.query.filter_by(id=pergunta_escolhida_id).first()
            return render_template('responder_perguntas.html', user=current_user, pergunta=pergunta_escolhida)
        else:
            flash("Você não tem permissão para fazer isso!", category="error")
            return redirect(url_for('views.home'))
