import uuid
import sys
import os

PY2 = sys.version_info[0] == 2


def tem_saldo_suficiente(saldo1, saldo2):
    retorno = False
    if saldo1 >= saldo2:
        retorno = True
    return retorno


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
