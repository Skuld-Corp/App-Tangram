def tem_saldo_suficiente(saldo1, saldo2):
    retorno = False
    if saldo1 >= saldo2:
        retorno = True
    return retorno


import sys

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
