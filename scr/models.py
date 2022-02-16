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

event.listen(Usuario.__table__, "after_create", inserir_coins_iniciais_func)
event.listen(Usuario.__table__, "after_create", trigger_create_coin)


class SenhaReset(db.Model):
    __tablename__ = "senhareset"
    id = db.Column(db.Integer, primary_key=True)
    reset_key = db.Column(db.String(128), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)
    user = db.relationship('Usuario', lazy='joined', passive_deletes=True)
    has_activated = db.Column(db.Boolean, default=False)