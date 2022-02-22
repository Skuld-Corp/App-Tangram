"""
Biblioteca que tem como funcionalidade armazenas funções. Retirando assim a criação de funções de outros locais
"""

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


# Gera uma key aleatória para resetar a senha
def gerar_key():
    return uuid.uuid4()


# pega do env o nome do email
def email_user():
    return os.getenv("email_user")


# pega do env a senha do email
def email_passw():
    return os.getenv("email_password")


# pega do env a ulr do site
def url_do_site():
    return os.getenv("url_site")


def atualizar_perfil_func(nome: str, email: str, senha: str) -> bool:
    """
    Atualiza o perfil do usuário fazendo uso do current user
    @param nome: Nome do usuário recebido através do form de atualizar
    @param email: Email do usuário recebido através do form de atualizar
    @param senha: Senha do usuário recebido através do form de atualizar
    @return: Retorna um bool, False caso não tenha atualização e True em caso de atualização
    """
    houve_atualizacao_de_dados = False
    if nome:
        current_user.nome = nome
        houve_atualizacao_de_dados = True
    if email:
        current_user.email = email
        houve_atualizacao_de_dados = True
    if senha:
        if len(senha) > 3:
            salt = bcrypt.gensalt()
            senha_cripto = bcrypt.hashpw(senha.encode('utf-8'), salt)
            current_user.senha = senha_cripto
            houve_atualizacao_de_dados = True
    return houve_atualizacao_de_dados


def eh_menor_que_essa_quantidade_de_caracters(palavra: str, quantidade: int) -> bool:
    """
    Função para verificar se a string é menor que a quantidade de caracters informados
    @param palavra: A palavra a ser verificada
    @param quantidade: A quantidade de caracters que deseja verificar
    @return: Retorna True em caso da palavra seja menor que a quantidade de caracters e False em caso negativo
    """
    tamanho = len(palavra)
    eh_menor = False
    if tamanho < quantidade:
        eh_menor = True
    return eh_menor


def atualizar_pergunta_func(pergunta, titulo, pergunta_questao, resposta_1, resposta_2, resposta_3, resposta_4, resposta_certa, questao_dificuldade):
    """
    Função para atualizar a pergunta
    @param pergunta: A pergunta extraida do DB (objeto)
    @param titulo: titulo extraido do form
    @param pergunta_questao: a questão da pergunta extraida do form
    @param resposta_1: a resposta 1 extraida do form
    @param resposta_2: a resposta 2 extraida do form
    @param resposta_3: a resposta 3 extraida do form
    @param resposta_4: a resposta 4 extraida do form
    @param resposta_certa: a resposta certa extraida do form
    @param questao_dificuldade: a dificuldade da questão extraida do form
    """
    pergunta.resposta_certa = resposta_certa
    pergunta.questao_dificuldade = questao_dificuldade
    if titulo:
        pergunta.pergunta_titulo = titulo
    if pergunta_questao:
        pergunta.pergunta = pergunta_questao
    if resposta_1:
        pergunta.resp_1 = resposta_1
    if resposta_2:
        pergunta.resp_2 = resposta_2
    if resposta_3:
        pergunta.resp_3 = resposta_3
    if resposta_4:
        pergunta.resp_4 = resposta_4
