import datetime as datetime

from . import db
from flask_login import UserMixin
from sqlalchemy import DDL, event
from .help_functions import RoleMixin


class Usuario(db.Model, UserMixin, RoleMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.LargeBinary)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'))
    saldo = db.relationship('TangramCoin', passive_deletes=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, nome, email, senha, role):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.role = role


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(150))


class TangramCoin(db.Model):
    __tablename__ = 'tangramcoin'
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))


class SenhaReset(db.Model):
    __tablename__ = "senhareset"
    id = db.Column(db.Integer, primary_key=True)
    reset_key = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)
    user = db.relationship('Usuario', lazy='joined', passive_deletes=True)
    has_activated = db.Column(db.Boolean, default=False)


class PerguntasQuiz(db.Model):
    __tablename__ = "perguntasquiz"
    id = db.Column(db.Integer, primary_key=True)
    professor_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    pergunta_titulo = db.Column(db.String(80))
    pergunta = db.Column(db.Text)
    resp_1 = db.Column(db.Text)
    resp_2 = db.Column(db.Text)
    resp_3 = db.Column(db.Text)
    resp_4 = db.Column(db.Text)
    resposta_certa = db.Column(db.Integer)
    questao_dificuldade = db.Column(db.String(20))


class PerguntasRespondidas(db.Model):
    __tablename__ = "perguntasrespondidas"
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    pergunta_id = db.Column(db.Integer, db.ForeignKey('perguntasquiz.id', ondelete='CASCADE'))


class PerguntasDesempenho(db.Model):
    __tablename__ = "perguntas_desempenho"
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'))
    total_de_perguntas_respondidas = db.Column(db.Integer)
    total_de_perguntas_acertadas = db.Column(db.Integer)


inserir_coins_iniciais_func = DDL("""\
    CREATE OR REPLACE FUNCTION inserir_coins_iniciais_func() 
    RETURNS trigger  AS $$
    BEGIN
        IF (NEW.role = '3') THEN
		    INSERT INTO tangramCoin (player_id, saldo) values (NEW.id, '100');
	    END IF;
	RETURN NEW;
    END;
$$ LANGUAGE plpgsql ; 
""")

trigger_create_coin = DDL('''\
    CREATE TRIGGER CoinsIniciais AFTER INSERT
    ON usuario 
    FOR EACH ROW 
    EXECUTE PROCEDURE inserir_coins_iniciais_func();
''')

inserir_dados_desempenho_func = DDL("""\
    CREATE OR REPLACE FUNCTION inserir_dados_desempenho_func() 
    RETURNS trigger  AS $$
    BEGIN
        IF (NEW.role = '3') THEN
		    INSERT INTO perguntas_desempenho (aluno_id, total_de_perguntas_respondidas, total_de_perguntas_acertadas) values (NEW.id, '0', '0');
	    END IF;
	RETURN NEW;
    END;
$$ LANGUAGE plpgsql ; 
""")

trigger_create_desempenho = DDL('''\
    CREATE TRIGGER desempenho_criar AFTER INSERT
    ON usuario 
    FOR EACH ROW 
    EXECUTE PROCEDURE inserir_dados_desempenho_func();
''')


event.listen(Usuario.__table__, "after_create", inserir_coins_iniciais_func)
event.listen(Usuario.__table__, "after_create", inserir_dados_desempenho_func)
event.listen(Usuario.__table__, "after_create", trigger_create_coin)
event.listen(Usuario.__table__, "after_create", trigger_create_desempenho)
