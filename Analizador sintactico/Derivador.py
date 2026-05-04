import nltk
from Gramatica import Gramatica


class Derivador:
    def __init__(self, gramatica: Gramatica):
        self._gramatica_original = gramatica
        self._gramatica_nltk = gramatica.to_nltk()
        self._pasos: list = []

    @property
    def pasos(self) -> list:
        return self._pasos

    def Derivar_izquierda(self, arbol: nltk.Tree):
        pasos = [str(arbol.label())]
        actual = [(arbol.label(), arbol)]

        while True:
            # Buscar el primer no terminal (Tree) de izquierda a derecha
            i = None
            for idx, (_, elemento) in enumerate(actual):
                if isinstance(elemento, nltk.Tree):
                    i = idx
                    break

            if i is None:
                break

            _, elemento = actual[i]

            # Expandir el nodo
            derivacion = []
            for hijo in elemento:
                if isinstance(hijo, nltk.Tree):
                    derivacion.append((hijo.label(), hijo))
                else:
                    # ✅ CORRECCIÓN: para terminales, guardar como string
                    derivacion.append((str(hijo), str(hijo)))

            actual = actual[:i] + derivacion + actual[i + 1:]
            pasos.append(" ".join(e for e, _ in actual))

        return pasos

    def Derivar_derecha(self, arbol: nltk.Tree):
        pasos = [str(arbol.label())]
        actual = [(arbol.label(), arbol)]

        while True:
            # Buscar el último no terminal (Tree) de derecha a izquierda
            i = None
            for idx, (_, elemento) in reversed(list(enumerate(actual))):
                if isinstance(elemento, nltk.Tree):
                    i = idx
                    break

            if i is None:
                break

            _, elemento = actual[i]

            # Expandir el nodo
            derivacion = []
            for hijo in elemento:
                if isinstance(hijo, nltk.Tree):
                    derivacion.append((hijo.label(), hijo))
                else:
                    # ✅ CORRECCIÓN: para terminales, guardar como string
                    derivacion.append((str(hijo), str(hijo)))

            actual = actual[:i] + derivacion + actual[i + 1:]
            pasos.append(" ".join(e for e, _ in actual))

        return pasos