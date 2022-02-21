import uuid
import sys
import os
from flask_login import current_user
import bcrypt

PY2 = sys.version_info[0] == 2


class RoleMixin(object):
    """
    "solução" para adicionar role ao flask login
    """

    if not PY2:  # pragma: no cover
        # Python 3 implicitly set __hash__ to None if we override __eq__
        # We set it back to its default implementation
        __hash__ = object.__hash__

    @property
    def has_role(self):
        return self.role


def gerar_key():
    return uuid.uuid4()


def email_user():
    return os.getenv("email_user")


def email_passw():
    return os.getenv("email_password")


def url_do_site():
    return os.getenv("url_site")


def campo_eh_vazio(campo):
    vazio = True
    if not campo == '':
        vazio = False
    return vazio


def atualizar_perfil_func(nome, email, senha):
    houve_atualizacao_de_dados = False
    if not campo_eh_vazio(nome):
        current_user.nome = nome
        houve_atualizacao_de_dados = True
    if not campo_eh_vazio(email):
        current_user.email = email
        houve_atualizacao_de_dados = True
    if not campo_eh_vazio(senha):
        if len(senha) > 3:
            salt = bcrypt.gensalt()
            senha_cripto = bcrypt.hashpw(senha.encode('utf-8'), salt)
            current_user.senha = senha_cripto
            houve_atualizacao_de_dados = True
    return houve_atualizacao_de_dados


def eh_menor_que_essa_quantidade_de_caracters(palavra, quantidade):
    tamanho = len(palavra)
    eh_menor = False
    if tamanho < quantidade:
        eh_menor = True
    return eh_menor


def atualizar_pergunta_func(pergunta, titulo, pergunta_questao, resposta_1, resposta_2, resposta_3, resposta_4, resposta_certa, questao_dificuldade):
    pergunta.resposta_certa = resposta_certa
    pergunta.questao_dificuldade = questao_dificuldade
    if not campo_eh_vazio(titulo):
        pergunta.pergunta_titulo = titulo
    if not campo_eh_vazio(pergunta_questao):
        pergunta.pergunta = pergunta_questao
    if not campo_eh_vazio(resposta_1):
        pergunta.resp_1 = resposta_1
    if not campo_eh_vazio(resposta_2):
        pergunta.resp_2 = resposta_2
    if not campo_eh_vazio(resposta_3):
        pergunta.resp_3 = resposta_3
    if not campo_eh_vazio(resposta_4):
        pergunta.resp_4 = resposta_4
