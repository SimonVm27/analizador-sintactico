
class NodoAST:
    def __init__(self ,valor: str, es_terminal: bool = False):
        self._valor=valor
        self._hijos= []
        self._es_terminal = es_terminal

    @property
    def valor(self):
        return self._valor
    @property
    def hijos(self):
        return self._hijos
    @property
    def es_terminal(self):
        return self._es_terminal

    def agg_hijo(self,hijo:'NodoAST'):
        self._hijos.append(hijo)


    def es_hoja(self) ->bool:
        return len(self._hijos) == 0




