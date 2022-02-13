from . import db
from flask_login import UserMixin
from sqlalchemy import DDL, event
from .help_functions import RoleMixin


class Usuario(db.Model, UserMixin, RoleMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'))
    saldo = db.relationship('TangramCoin')

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
    __tablename__ = 'tangramCoin'
    id = db.Column(db.Integer, primary_key=True)
    saldo = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))


trigger_create_coin = DDL('''\
    CREATE TRIGGER CoinsIniciais AFTER INSERT
    ON usuario 
    FOR EACH ROW 
        begin
            If (NEW.`role` = '3') THEN
		        INSERT INTO tangramcoin (player_id, saldo) values (NEW.id, '100');
	        END IF;
	end;
''')

event.listen(Usuario.__table__, "after_create", trigger_create_coin)
