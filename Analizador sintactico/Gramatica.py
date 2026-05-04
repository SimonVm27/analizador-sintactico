import nltk
class Gramatica:
    def __init__(self, texto: str):
        self.producciones = {}
        self.no_terminales = set()
        self.terminales = set()
        self.simbolo_inicial = None

        self._procesar(texto)

    def _procesar(self, texto: str):
        lineas = [l.strip() for l in texto.strip().split("\n") if l.strip()]


        for i, linea in enumerate(lineas):
            izquierda = linea.split("->")[0].strip()

            if i == 0:
                self.simbolo_inicial = izquierda

            self.no_terminales.add(izquierda)


        for linea in lineas:
            izquierda, derecha = linea.split("->")
            izquierda = izquierda.strip()

            partes = derecha.split("|")
            lista_producciones = []

            for parte in partes:
                simbolos = parte.strip().split()
                lista_producciones.append(simbolos)

                for s in simbolos:
                    if s not in self.no_terminales:
                        self.terminales.add(s)

            self.producciones[izquierda] = lista_producciones



    def es_no_terminal(self, simbolo):
        return simbolo in self.no_terminales

    def es_terminal(self, simbolo):
        return simbolo in self.terminales

    def obtener_producciones(self, simbolo):
        return self.producciones.get(simbolo, [])

    def to_nltk(self):
        lineas = []
        for izquierda, producciones in self.producciones.items():
            for prod in producciones:
                # Agregar comillas si es terminal y no tiene
                prod_con_comillas = []
                for simbolo in prod:
                    if simbolo in self.terminales:
                        prod_con_comillas.append(f"'{simbolo}'")
                    else:
                        prod_con_comillas.append(simbolo)
                lineas.append(f"{izquierda} -> {' '.join(prod_con_comillas)}")
        return nltk.CFG.fromstring("\n".join(lineas))