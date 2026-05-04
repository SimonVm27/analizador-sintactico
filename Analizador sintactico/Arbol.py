import Gramatica
import nltk
from nltk import CFG
from nltk.parse import ChartParser
from NodoAST import NodoAST
class Arbol:
    def __init__(self, Gramatica:Gramatica):
        self._gramatica = Gramatica.to_nltk()

    def gen_arbol (self, expresion: str):
        tokens = expresion.split()
        gen= ChartParser(self._gramatica)
        arboles = list(gen.parse(tokens))

        if not arboles:
            raise ValueError("La expresion no pertenece a la gramatica")
        arbol = arboles[0]
        return arbol


    def transformar (self, arbol:nltk.Tree)-> NodoAST:
        if isinstance(arbol, nltk.Tree):
            raiz = NodoAST(arbol.label(), es_terminal =False)
            for hijo in arbol:
                raiz.agg_hijo(self.transformar(hijo))
            return raiz
        else:
            return NodoAST(str(arbol),es_terminal = True)

