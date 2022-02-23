import pytz
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user
from .models import SenhaReset, PerguntasQuiz, PerguntasRespondidas, PerguntasDesempenho
import datetime
from random import choice


views = Blueprint('views', __name__)


@views.route('/')
def home():
    """
    Home page
    @return: retorna o html da home page OU redireciona para login caso não esteja logado
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        #return redirect(url_for('views.login'))
        return render_template('auth/cadastro.html', user=current_user)
    else:
        if current_user.has_role == 3:
            desempenho = PerguntasDesempenho.query.filter_by(aluno_id=current_user.id).first()
            return render_template('home.html', user=current_user, desempenho=desempenho)
        else:
            desempenho = None
            return render_template('home.html', user=current_user, desempenho=desempenho)


@views.route('/cadastro')
def cadastro():
    """
    Rota de cadastro
    @return: retorna o template de cadastro
    """
    return render_template('auth/cadastro.html', user=current_user)


@views.route('/login')
def login():
    """
    Rota de login, Caso um usuario admin acesse essa rota ira cadastrar um professor ao invés do aluno (default)
    @return: Retorna a pagina de login OU redireciona pra home caso já esteja logado.
    """
    if current_user.is_authenticated:
        flash('Você já esta logado!', category="sucess")
        return redirect(url_for('views.home'))
    else:
        return render_template('auth/login.html', user=current_user)


@views.route('/reset-senha')
def reset_senha():
    """
    Rota para solicitar o reset da senha
    @return: Retorna para home page, caso esteja logado. Caso não esteja logado, retorna o template para solicitar o reset da senha
    """
    if current_user.is_authenticated:
        flash('Você já esta logado!', category="sucess")
        return redirect(url_for('views.home'))
    else:
        return render_template('reset_password/esqueceu_senha_solicitar.html')


@views.route('/trocar-senha/<id>', methods=['GET',])
def nova_senha_get(id):
    """
    Rota para resetar a senha do usuario. Link enviado por email
    @param id: id unico gerado aleatoriamente e enviado por email
    @return: Verifica se o id gerado é valido, caso sim verifica também o prazo de validade do id.
    Em caso de tudo positivo retorna o template pra resetar a senha
    """
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
        return render_template("reset_password/nova_senha.html", id=chave)
    else:
        flash("Não foi possível localizar esse endereço", category="error")
        return redirect(url_for("views.home"))


@views.route('/perfil')
def perfil():
    """
    Rota de perfil do usuario
    @return: Retorna o template de perfil com os dados do usuario
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        return render_template('perfil.html', user=current_user)


@views.route('/nova-pergunta')
def nova_pergunta():
    """
    Rota para criação de novas perguntas, verifica se o usuario é professor para a criação de perguntas
    @return: Retorna em caso positivo, o html para a criação de perguntas. Em caso negativo redireciona pra home
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        if current_user.has_role == 2:
            return render_template('professor_perguntas/criar_perguntas.html', user=current_user)
        else:
            flash("Você não tem permissão para fazer isso!", category="error")
            return redirect(url_for('views.home'))


@views.route("/quiz")
def responder_quiz():
    """
    Rota para o aluno responder as perguntas. Em caso da pessoa não ser do tipo aluno será redirecionada pra home
    @return: Retorna o html com as perguntas pro aluno responder
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!", category="error")
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
            else:
                pergunta_escolhida_id = choice(tuple(perguntas_nao_respondidas))
                pergunta_escolhida = PerguntasQuiz.query.filter_by(id=pergunta_escolhida_id).first()
                return render_template('aluno_perguntas/responder_perguntas.html', user=current_user, pergunta=pergunta_escolhida)
        else:
            flash("Você não tem permissão para fazer isso!", category="error")
            return redirect(url_for('views.home'))


@views.route("/suas_perguntas")
def perguntas_dash():
    """
    Rota que mostrar todas as perguntas registrada pelo professor
    @return: Retorna o html com todas as perguntas registrada pelo professor
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!", category="error")
        return redirect(url_for('views.login'))
    else:
        if current_user.has_role == 2:
            perguntas_do_professor = PerguntasQuiz.query.filter_by(professor_id=current_user.id).all()
            return render_template("professor_perguntas/perguntas_dash.html", user=current_user, perguntas=perguntas_do_professor)
        else:
            flash("Você não tem permissao para acessar essa pagina!", category="error")
            return redirect(url_for('views.home'))


@views.route('/editar_pergunta/<id>', methods=['GET',])
def editar_pergunta(id):
    """
    Rota que mostra a pergunta do professor para ser editada
    @param id: Id da pergunta no DB
    @return: Retorna o html com os dados da pergunta para o professor editar.
    """
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!", category="error")
        return redirect(url_for('views.login'))
    else:
        try:
            pergunta = PerguntasQuiz.query.filter_by(id=id).first()
            pergunta_pertence_ao_professor = pergunta.professor_id == current_user.id
            if current_user.has_role == 2 and pergunta_pertence_ao_professor:
                return render_template('professor_perguntas/editar_pergunta.html', user=current_user, pergunta=pergunta)
            else:
                flash("Você não tem permissao para acessar essa pagina!", category="error")
                return redirect(url_for('views.home'))
        except:
            flash("Ops ocorreu algum erro!", category="error")
            return redirect(url_for('views.home'))
