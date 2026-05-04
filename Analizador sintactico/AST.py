# AST.py
from NodoAST import NodoAST
import nltk

class AST:
    def __init__(self, arbol: nltk.Tree, raiz: NodoAST):
        self._arbol = arbol
        self._Raiz  = raiz

    OPERADORES = {'+', '-', '*', '/'}
    IGNORAR    = {'(', ')'}

    @property
    def arbol(self):
        return self._arbol

    def reducir(self, nodo: NodoAST) -> NodoAST:
        # Hoja terminal
        if nodo.es_hoja():
            if nodo.valor in self.IGNORAR:
                return None
            return NodoAST(nodo.valor, es_terminal=True)

        # Reducir hijos
        hijos = [h for i in nodo.hijos
                 if (h := self.reducir(i)) is not None]

        if len(hijos) == 0:
            return None


        if len(hijos) == 1:
            return hijos[0]

        # Buscar operador
        ops      = [h for h in hijos if h.valor in self.OPERADORES and h.es_hoja()]
        operandos = [h for h in hijos if h not in ops]

        if len(ops) == 1:
            raiz_op = NodoAST(ops[0].valor, es_terminal=False)
            for op in operandos:
                raiz_op.agg_hijo(op)
            return raiz_op

        return hijos[0]