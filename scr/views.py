import pytz
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import SenhaReset
import datetime

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if not current_user.is_authenticated:
        flash("Por favor, logue para acessar essa página!")
        return redirect(url_for('views.login'))
    else:
        return render_template('home.html', user=current_user)


@views.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', user=current_user)


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