<div align="center">

# 🌳 CFG Tree Generator

### Generador visual de árboles sintácticos para gramáticas independientes del contexto

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![NLTK](https://img.shields.io/badge/NLTK-NLP-4B8BBE?style=for-the-badge)](https://www.nltk.org/)
[![License](https://img.shields.io/badge/License-MIT-E94560?style=for-the-badge)](LICENSE)

---

*Una herramienta interactiva para definir gramáticas CFG, analizar expresiones y visualizar sus árboles de derivación (Parse Tree) y árboles de sintaxis abstracta (AST) en tiempo real.*

</div>

---

## 📋 Tabla de Contenidos

- [¿Qué es esto?](#-qué-es-esto)
- [Características](#-características)
- [Capturas de pantalla](#-capturas-de-pantalla)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Arquitectura](#-arquitectura)
- [Gramática por defecto](#-gramática-por-defecto)

---

## 🔍 ¿Qué es esto?

**CFG Tree Generator** es una aplicación de escritorio orientada al aprendizaje de **teoría de lenguajes formales y compiladores**. Permite al usuario:

1. Definir cualquier **gramática libre de contexto (CFG)** en notación BNF simplificada.
2. Ingresar una expresión y verificar si **pertenece al lenguaje** generado por esa gramática.
3. Visualizar paso a paso la **derivación por la izquierda o por la derecha**.
4. Obtener y renderizar el **árbol de análisis sintáctico (Parse Tree)** completo.
5. Obtener y renderizar el **árbol de sintaxis abstracta (AST)** reducido, eliminando nodos innecesarios.

Es útil para estudiantes y docentes de **compiladores, autómatas y lenguajes formales**.

---

## ✨ Características

| Función | Descripción |
|---|---|
| 📝 **Editor de gramática** | Define tu propia CFG con notación `->` y `\|` para alternativas |
| 🔄 **Derivación izquierda / derecha** | Visualiza los pasos de derivación en ambas direcciones |
| 🌲 **Parse Tree visual** | Árbol de análisis sintáctico concreto con nodos coloreados |
| 🧠 **AST reducido** | Árbol de sintaxis abstracta limpio, sin nodos intermedios innecesarios |
| ⚡ **Procesamiento asíncrono** | Worker thread dedicado — la UI nunca se congela |
| 🎨 **Interfaz dark mode** | UI moderna con paleta de colores oscura y diseño limpio |
| 🔧 **Autoformato de expresiones** | Detecta y corrige el espaciado de operadores automáticamente |
| 📐 **Zoom y scroll** | Las vistas de árbol son interactivas y se adaptan al tamaño de la ventana |

---

## 🖥️ Capturas de pantalla

> La aplicación presenta una interfaz dividida en dos paneles:
> - **Panel izquierdo:** editor de gramática, campo de expresión y selector de derivación.
> - **Panel derecho:** pestañas con el Parse Tree, el AST y los pasos de derivación detallados.

```
┌─────────────────────────────────────────────────────────────┐
│  🌳  CFG Tree Generator                                      │
├──────────────────┬──────────────────────────────────────────┤
│  📝 Gramática    │  [ Parse Tree ] [ AST ] [ Derivación ]   │
│                  │                                          │
│  E -> E + T | T  │         E                               │
│  T -> T * F | F  │        /|\                              │
│  F -> ( E ) | a  │       E + T                             │
│                  │      /    \                             │
│  Expresión:      │     T      F                            │
│  [ a + b * c   ] │     |      |                            │
│                  │     F      c                            │
│  ○ Izquierda     │     |                                   │
│  ● Derecha       │     a                                   │
│                  │                                          │
│  [ Generar ]     │                                          │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 🚀 Instalación

### Prerequisitos

- Python **3.8** o superior
- pip

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/cfg-tree-generator.git
cd cfg-tree-generator

# 2. (Opcional) Crea un entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Descarga los datos de NLTK necesarios (solo la primera vez)
python -c "import nltk; nltk.download('punkt')"

# 5. Ejecuta la aplicación
python ventana_principal.py
```

---

## 🎮 Uso

### 1. Define tu gramática
En el panel izquierdo escribe tu CFG usando la notación:
```
E -> E + T | E - T | T
T -> T * F | T / F | F
F -> ( E ) | a | b | c
```
- El **primer símbolo** de la primera regla se toma como símbolo inicial.
- Las alternativas se separan con `|`.
- Los terminales se escriben en minúscula o como símbolos; los no terminales en mayúscula.

### 2. Ingresa una expresión
Escribe la expresión a analizar en el campo de texto, por ejemplo:
```
a + b * c
```
> 💡 **Autoformato:** si escribes `a+b*c`, la app detecta los operadores pegados y los separa automáticamente.

### 3. Selecciona el tipo de derivación
- **Derivación por la izquierda:** expande siempre el no terminal más a la izquierda.
- **Derivación por la derecha:** expande siempre el no terminal más a la derecha.

### 4. Genera
Haz clic en **Generar** y observa en las pestañas:
- 🌲 **Parse Tree** — árbol de derivación completo.
- 🧠 **AST** — árbol simplificado con solo operadores y operandos.
- 📋 **Derivación** — lista paso a paso del proceso de derivación.

---

## 📁 Estructura del proyecto

```
cfg-tree-generator/
│
├── ventana_principal.py   # Interfaz gráfica (PyQt5), lógica de UI y worker thread
├── Gramatica.py           # Parser y representación interna de gramáticas CFG
├── Arbol.py               # Generación del Parse Tree usando NLTK ChartParser
├── Derivador.py           # Derivaciones izquierda y derecha paso a paso
├── AST.py                 # Reducción del Parse Tree al AST
├── NodoAST.py             # Nodo genérico del árbol (estructura de datos)
│
├── requirements.txt       # Dependencias del proyecto
├── .gitignore             # Archivos ignorados por Git
└── README.md              # Este archivo
```

---

## 🏗️ Arquitectura

```
ventana_principal.py
    │
    ├── WorkerThread (QThread)
    │       │
    │       ├── Gramatica ──────► Parser BNF → estructura interna + NLTK CFG
    │       │
    │       ├── Arbol ──────────► ChartParser → nltk.Tree
    │       │
    │       ├── Derivador ──────► Derivación izquierda / derecha → list[str]
    │       │
    │       └── AST ────────────► Reducción nltk.Tree → NodoAST simplificado
    │
    └── DibujadorArbol
            ├── dibujar_parse_tree(nltk.Tree, QGraphicsScene)
            └── dibujar_ast(NodoAST, QGraphicsScene)
```

### Módulos

| Módulo | Responsabilidad |
|---|---|
| `NodoAST` | Nodo de árbol genérico con valor, hijos y flag de terminal |
| `Gramatica` | Parsea texto BNF, clasifica terminales/no terminales y convierte a `nltk.CFG` |
| `Arbol` | Usa `ChartParser` de NLTK para generar el `nltk.Tree` y lo convierte a `NodoAST` |
| `Derivador` | Recorre el `nltk.Tree` para producir los pasos de derivación izquierda o derecha |
| `AST` | Reduce el árbol concreto eliminando paréntesis y nodos unitarios, dejando solo operadores y operandos |
| `ventana_principal` | Orquesta todo en una UI PyQt5 con procesamiento en hilo secundario |

---

## 📐 Gramática por defecto

La aplicación incluye una gramática de expresiones aritméticas como ejemplo:

```
E -> E + T | E - T | T
T -> T * F | T / F | F
F -> ( E ) | a | b | ... | z | A | B | ... | Z | 0 | 1 | ... | 9
```

Esta gramática reconoce expresiones con suma, resta, multiplicación y división, con precedencia correcta de operadores y soporte para paréntesis, letras y dígitos como operandos.

---

## 🛠️ Tecnologías utilizadas

- **[Python 3](https://www.python.org/)** — lenguaje base
- **[PyQt5](https://riverbankcomputing.com/software/pyqt/)** — interfaz gráfica de escritorio
- **[NLTK](https://www.nltk.org/)** — parsing de gramáticas CFG con `ChartParser`

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

Hecho con ❤️ para el aprendizaje de teoría de compiladores

</div>
