from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user


views = Blueprint('views', __name__)


@views.route('/')
def home():
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