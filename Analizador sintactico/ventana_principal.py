# ventana_principal.py

import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QRadioButton, QButtonGroup,
    QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsPathItem,
    QGroupBox, QSplitter, QStatusBar, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QThread, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPen, QBrush, QPainter, QPainterPath
)
import nltk

from Gramatica import Gramatica
from Arbol import Arbol
from Derivador import Derivador
from NodoAST import NodoAST
from AST import AST

# ── Paleta ───────────────────────────────────────────────────────────────────
_BG_APP      = "#1A1A2E"
_BG_PANEL    = "#16213E"
_BG_INPUT    = "#0F3460"
_ACCENT      = "#E94560"
_ACCENT_DARK = "#C73652"
_ACCENT_SOFT = "#533483"
_TEXT_DARK   = "#E0E0E0"
_TEXT_MED    = "#A0A0B0"

# ── Config nodos ─────────────────────────────────────────────────────────────
_W   = 52
_H   = 30
_RB  = 8
_SH  = 75
_SV  = 75

_C_NT       = QColor("#533483")
_C_NT_B     = QColor("#7B52AB")
_C_T        = QColor("#E94560")
_C_T_B      = QColor("#FF6B6B")
_C_AST_NT   = QColor("#0D5C8C")
_C_AST_NT_B = QColor("#2E86C1")
_C_AST_T    = QColor("#117A65")
_C_AST_T_B  = QColor("#1ABC9C")
_C_TXT      = QColor("#FFFFFF")
_C_LINE_PT  = QColor("#7B52AB")
_C_LINE_AST = QColor("#2E86C1")
_C_BG       = QColor("#1A1A2E")

# ── Gramática por defecto ─────────────────────────────────────────────────────
_min = " | ".join(list("abcdefghijklmnopqrstuvwxyz"))
_may = " | ".join(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
_dig = " | ".join(list("0123456789"))
GRAMATICA_DEFAULT = (
    "E -> E + T | E - T | T\n"
    "T -> T * F | T / F | F\n"
    f"F -> ( E ) | {_min} | {_may} | {_dig}"
)


# ══════════════════════════════════════════════════════════════════════════════
#  DIBUJADOR
# ══════════════════════════════════════════════════════════════════════════════
class DibujadorArbol:

    def _nodo(self, scene: QGraphicsScene, x: float, y: float,
              texto: str, es_terminal: bool, es_ast: bool = False) -> QPointF:
        if es_ast:
            cf = _C_AST_T   if es_terminal else _C_AST_NT
            cb = _C_AST_T_B if es_terminal else _C_AST_NT_B
        else:
            cf = _C_T   if es_terminal else _C_NT
            cb = _C_T_B if es_terminal else _C_NT_B

        rx, ry = x - _W / 2, y - _H / 2
        path = QPainterPath()
        path.addRoundedRect(QRectF(rx, ry, _W, _H), _RB, _RB)
        item = QGraphicsPathItem(path)
        item.setBrush(QBrush(cf))
        item.setPen(QPen(cb, 2))
        scene.addItem(item)

        lbl = scene.addText(texto)
        lbl.setDefaultTextColor(_C_TXT)
        lbl.setFont(QFont("Consolas", 9, QFont.Bold))
        br = lbl.boundingRect()
        lbl.setPos(x - br.width() / 2, y - br.height() / 2)

        return QPointF(x, y)

    def _linea(self, scene: QGraphicsScene, padre: QPointF, hijo: QPointF,
               es_ast: bool = False):
        color = _C_LINE_AST if es_ast else _C_LINE_PT
        p = QPainterPath()
        p.moveTo(padre.x(), padre.y() + _H / 2)
        my = (padre.y() + hijo.y()) / 2
        p.cubicTo(padre.x(), my, hijo.x(), my, hijo.x(), hijo.y() - _H / 2)
        item = QGraphicsPathItem(p)
        item.setPen(QPen(color, 1.5))
        scene.addItem(item)

    # ── Parse Tree ────────────────────────────────────────────────────────────
    def _pt_rec(self, scene, nodo, nivel: int, offset: list) -> QPointF:
        if isinstance(nodo, str):
            x = offset[0] * _SH
            y = nivel * _SV
            c = self._nodo(scene, x, y, nodo, True, False)
            offset[0] += 1
            return c

        hijos_c = [self._pt_rec(scene, hijo, nivel + 1, offset) for hijo in nodo]
        xp = (hijos_c[0].x() + hijos_c[-1].x()) / 2 if hijos_c else offset[0] * _SH
        yp = nivel * _SV
        cp = self._nodo(scene, xp, yp, nodo.label(), False, False)
        for ch in hijos_c:
            self._linea(scene, cp, ch, False)
        return cp

    def dibujar_parse_tree(self, arbol_nltk, scene: QGraphicsScene):
        scene.clear()
        scene.setBackgroundBrush(QBrush(_C_BG))
        self._pt_rec(scene, arbol_nltk, 0, [0])
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))

    # ── AST ───────────────────────────────────────────────────────────────────
    def _ast_rec(self, scene, nodo: NodoAST, nivel: int, offset: list) -> QPointF:
        if nodo.es_hoja():
            x = offset[0] * _SH
            y = nivel * _SV
            c = self._nodo(scene, x, y, nodo.valor, True, True)
            offset[0] += 1
            return c

        hijos_c = [self._ast_rec(scene, hijo, nivel + 1, offset)
                   for hijo in nodo.hijos]
        xp = (hijos_c[0].x() + hijos_c[-1].x()) / 2 if hijos_c else offset[0] * _SH
        yp = nivel * _SV
        cp = self._nodo(scene, xp, yp, nodo.valor, False, True)
        for ch in hijos_c:
            self._linea(scene, cp, ch, True)
        return cp

    def dibujar_ast(self, nodo_ast: NodoAST, scene: QGraphicsScene):
        scene.clear()
        scene.setBackgroundBrush(QBrush(_C_BG))
        self._ast_rec(scene, nodo_ast, 0, [0])
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))


# ══════════════════════════════════════════════════════════════════════════════
#  WORKER THREAD
# ══════════════════════════════════════════════════════════════════════════════
class WorkerThread(QThread):
    resultado = pyqtSignal(list, object, object)
    error     = pyqtSignal(str)

    def __init__(self, texto_gram: str, expresion: str, izquierda: bool):
        super().__init__()
        self.texto_gram = texto_gram
        self.expresion  = expresion
        self.izquierda  = izquierda

    def run(self):
        try:
            gram       = Gramatica(self.texto_gram)
            arbol_obj  = Arbol(gram)
            arbol_nltk = arbol_obj.gen_arbol(self.expresion)

            derivador = Derivador(gram)
            pasos = (derivador.Derivar_izquierda(arbol_nltk)
                     if self.izquierda
                     else derivador.Derivar_derecha(arbol_nltk))

            nodo_concreto = arbol_obj.transformar(arbol_nltk)
            ast_obj       = AST(arbol_nltk, nodo_concreto)
            nodo_ast      = ast_obj.reducir(nodo_concreto)

            self.resultado.emit(pasos, arbol_nltk, nodo_ast)
        except Exception as e:
            self.error.emit(str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Árboles Sintácticos")
        self.setMinimumSize(1150, 720)
        self._dibujador = DibujadorArbol()
        self._worker    = None
        self._build_ui()
        self._apply_styles()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        vlay = QVBoxLayout(root)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)

        vlay.addWidget(self._make_header())
        vlay.addWidget(self._make_toolbar())

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._make_left_panel())
        splitter.addWidget(self._make_right_panel())
        splitter.setSizes([330, 820])
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(
            f"QSplitter::handle{{background:{_ACCENT_SOFT};}}")
        vlay.addWidget(splitter, 1)

        self._sb = QStatusBar()
        self._sb.setStyleSheet(
            f"QStatusBar{{background:{_BG_PANEL};color:{_TEXT_MED};"
            f"font-size:12px;border-top:1px solid {_ACCENT_SOFT};}}")
        self.setStatusBar(self._sb)
        self._sb.showMessage(
            "Listo — ingresa una expresión y pulsa Generar")

    def _make_header(self):
        f = QFrame()
        f.setFixedHeight(54)
        f.setStyleSheet(
            f"background:{_BG_PANEL};border-bottom:2px solid {_ACCENT};")
        lay = QHBoxLayout(f)
        lay.setContentsMargins(20, 0, 20, 0)

        ico = QLabel("⬡")
        ico.setStyleSheet(f"color:{_ACCENT};font-size:22px;")
        tit = QLabel("Generador de Árboles Sintácticos")
        tit.setStyleSheet(
            f"color:{_TEXT_DARK};font-size:16px;"
            f"font-weight:bold;letter-spacing:1px;")

        self._lbl_estado = QLabel("● Listo")
        self._lbl_estado.setStyleSheet(
            "color:#00D4AA;font-size:13px;font-weight:bold;")

        lay.addWidget(ico)
        lay.addSpacing(10)
        lay.addWidget(tit)
        lay.addStretch()
        lay.addWidget(self._lbl_estado)
        return f

    def _make_toolbar(self):
        f = QFrame()
        f.setFixedHeight(62)
        f.setStyleSheet(
            f"background:{_BG_APP};"
            f"border-bottom:1px solid {_ACCENT_SOFT};")
        lay = QHBoxLayout(f)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(12)

        lbl = QLabel("Expresión:")
        lbl.setStyleSheet(f"color:{_TEXT_MED};font-size:13px;")

        self._inp = QLineEdit()
        self._inp.setPlaceholderText(
            "Ej: a + b * c  |  5 + ( X - Y ) * Z  |  x+y  (se autoformatea)")
        self._inp.setFixedHeight(36)
        self._inp.setMinimumWidth(300)
        self._inp.returnPressed.connect(self._generar)

        lbl2 = QLabel("Derivación:")
        lbl2.setStyleSheet(f"color:{_TEXT_MED};font-size:13px;")

        self._rb_izq = QRadioButton("⬅ Izquierda")
        self._rb_der = QRadioButton("Derecha ➡")
        self._rb_izq.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self._rb_izq)
        grp.addButton(self._rb_der)

        self._btn_gen = QPushButton("⚡  Generar")
        self._btn_gen.setFixedHeight(36)
        self._btn_gen.setCursor(Qt.PointingHandCursor)
        self._btn_gen.clicked.connect(self._generar)

        btn_lim = QPushButton("✕  Limpiar")
        btn_lim.setFixedHeight(36)
        btn_lim.setCursor(Qt.PointingHandCursor)
        btn_lim.clicked.connect(self._limpiar)

        lay.addWidget(lbl)
        lay.addWidget(self._inp, 2)
        lay.addSpacing(6)
        lay.addWidget(lbl2)
        lay.addWidget(self._rb_izq)
        lay.addWidget(self._rb_der)
        lay.addSpacing(6)
        lay.addWidget(self._btn_gen)
        lay.addWidget(btn_lim)
        return f

    def _make_left_panel(self):
        w = QWidget()
        w.setStyleSheet(f"background:{_BG_APP};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 6, 12)
        lay.setSpacing(10)

        grp_g = QGroupBox("Gramática CFG")
        gl = QVBoxLayout(grp_g)
        self._txt_gram = QTextEdit()
        self._txt_gram.setPlainText(GRAMATICA_DEFAULT)
        self._txt_gram.setFont(QFont("Consolas", 9))
        self._txt_gram.setFixedHeight(130)
        gl.addWidget(self._txt_gram)
        lay.addWidget(grp_g)

        grp_p = QGroupBox("Pasos de Derivación")
        pl = QVBoxLayout(grp_p)
        self._txt_pasos = QTextEdit()
        self._txt_pasos.setReadOnly(True)
        self._txt_pasos.setFont(QFont("Consolas", 10))
        pl.addWidget(self._txt_pasos)

        btn_copy = QPushButton("📋  Copiar pasos")
        btn_copy.setFixedHeight(28)
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.clicked.connect(
            lambda: QApplication.clipboard().setText(
                self._txt_pasos.toPlainText()))
        pl.addWidget(btn_copy)
        lay.addWidget(grp_p, 1)
        return w

    def _make_right_panel(self):
        w = QWidget()
        w.setStyleSheet(f"background:{_BG_APP};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(6, 12, 12, 12)
        lay.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        self._scene_pt = QGraphicsScene()
        self._scene_pt.setBackgroundBrush(QBrush(_C_BG))
        self._view_pt  = QGraphicsView(self._scene_pt)
        self._view_pt.setRenderHint(QPainter.Antialiasing)
        self._view_pt.setRenderHint(QPainter.SmoothPixmapTransform)
        self._view_pt.setDragMode(QGraphicsView.ScrollHandDrag)
        self._view_pt.setStyleSheet(f"background:{_BG_APP};border:none;")
        self._tabs.addTab(self._view_pt, "🌳 Árbol de Derivación")

        self._scene_ast = QGraphicsScene()
        self._scene_ast.setBackgroundBrush(QBrush(_C_BG))
        self._view_ast  = QGraphicsView(self._scene_ast)
        self._view_ast.setRenderHint(QPainter.Antialiasing)
        self._view_ast.setRenderHint(QPainter.SmoothPixmapTransform)
        self._view_ast.setDragMode(QGraphicsView.ScrollHandDrag)
        self._view_ast.setStyleSheet(f"background:{_BG_APP};border:none;")
        self._tabs.addTab(self._view_ast, "✨ AST")

        lay.addWidget(self._tabs)
        return w

    # ── Estilos ───────────────────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background:{_BG_APP};
            color:{_TEXT_DARK};
            font-family:'Segoe UI','Ubuntu',sans-serif;
            font-size:13px;
        }}
        QLineEdit {{
            background:{_BG_INPUT};
            border:1.5px solid {_ACCENT_SOFT};
            border-radius:8px;
            padding:4px 10px;
            color:{_TEXT_DARK};
        }}
        QLineEdit:focus {{ border-color:{_ACCENT}; }}
        QTextEdit {{
            background:{_BG_INPUT};
            border:1.5px solid {_ACCENT_SOFT};
            border-radius:8px;
            padding:6px;
            color:{_TEXT_DARK};
            selection-background-color:{_ACCENT};
        }}
        QGroupBox {{
            background:{_BG_PANEL};
            border:none;
            border-radius:10px;
            margin-top:16px;
            padding:8px;
        }}
        QGroupBox::title {{
            color:#9B72D4;
            font-weight:bold;
            subcontrol-origin:margin;
            left:12px;
            top:-2px;
            font-size:12px;
        }}
        QPushButton {{
            background:{_BG_INPUT};
            color:{_TEXT_DARK};
            border:1px solid {_ACCENT_SOFT};
            border-radius:8px;
            padding:4px 14px;
        }}
        QPushButton:hover {{
            background:{_ACCENT_SOFT};
            border-color:{_ACCENT};
        }}
        QRadioButton {{
            background:{_BG_INPUT};
            color:{_TEXT_DARK};
            border:1.5px solid {_ACCENT_SOFT};
            border-radius:8px;
            padding:5px 14px;
            spacing:0px;
        }}
        QRadioButton:checked {{
            background:{_ACCENT_SOFT};
            border-color:{_ACCENT};
        }}
        QRadioButton::indicator {{ width:0px; height:0px; }}
        QTabWidget::pane {{ border:none; background:{_BG_APP}; }}
        QTabBar::tab {{
            background:{_BG_INPUT};
            color:{_TEXT_MED};
            border-radius:8px 8px 0 0;
            padding:8px 22px;
            margin-right:3px;
        }}
        QTabBar::tab:selected {{
            background:{_ACCENT};
            color:white;
            font-weight:bold;
        }}
        QScrollBar:vertical {{
            background:{_BG_APP}; width:6px; border-radius:3px;
        }}
        QScrollBar::handle:vertical {{
            background:{_ACCENT_SOFT}; border-radius:3px; min-height:20px;
        }}
        QScrollBar:horizontal {{
            background:{_BG_APP}; height:6px; border-radius:3px;
        }}
        QScrollBar::handle:horizontal {{
            background:{_ACCENT_SOFT}; border-radius:3px; min-width:20px;
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{ width:0; height:0; }}
        """)

        self._btn_gen.setStyleSheet(f"""
        QPushButton {{
            background:{_ACCENT};
            color:white;
            border:none;
            border-radius:10px;
            font-weight:bold;
            font-size:13px;
            padding:0 20px;
            min-width:120px;
        }}
        QPushButton:hover {{ background:{_ACCENT_DARK}; }}
        QPushButton:disabled {{ background:#444; color:#777; }}
        """)

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _autoformatear(self, expr: str) -> str:
        res = ""
        for ch in expr:
            res += f" {ch} " if ch in "+-*/()" else ch
        return re.sub(r'\s+', ' ', res).strip()

    def _necesita_formato(self, expr: str) -> bool:
        tokens = expr.split()
        for t in tokens:
            if any(op in t for op in "+-*/()") and len(t) > 1:
                return True
        if len(tokens) == 1 and any(c in expr for c in "+-*/()"):
            return True
        return False

    def _generar(self):
        if self._worker and self._worker.isRunning():
            return

        gram_txt = self._txt_gram.toPlainText().strip()
        if not gram_txt:
            QMessageBox.warning(self, "Error",
                                "La gramática no puede estar vacía.")
            return

        expr = self._inp.text().strip()
        if not expr:
            QMessageBox.warning(self, "Error",
                                "La expresión no puede estar vacía.")
            return

        if self._necesita_formato(expr):
            expr = self._autoformatear(expr)
            self._inp.setText(expr)
            self._sb.showMessage(f"Expresión autoformateada → {expr}")

        self._set_calculando(True)
        self._worker = WorkerThread(gram_txt, expr, self._rb_izq.isChecked())
        self._worker.resultado.connect(self._on_resultado)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_resultado(self, pasos, arbol_nltk, nodo_ast):
        self._set_calculando(False)
        tipo = "Izquierda" if self._rb_izq.isChecked() else "Derecha"

        # Pasos de derivación
        txt = f"── Derivación por {tipo} ──\n\n{pasos[0]}\n"
        for p in pasos[1:]:
            txt += f"\n⇒  {p}\n"
        self._txt_pasos.setPlainText(txt)

        # Parse Tree
        self._dibujador.dibujar_parse_tree(arbol_nltk, self._scene_pt)
        self._view_pt.fitInView(
            self._scene_pt.sceneRect(), Qt.KeepAspectRatio)

        # AST
        if nodo_ast is not None:
            self._dibujador.dibujar_ast(nodo_ast, self._scene_ast)
            self._view_ast.fitInView(
                self._scene_ast.sceneRect(), Qt.KeepAspectRatio)
        else:
            self._scene_ast.clear()
            self._scene_ast.setBackgroundBrush(QBrush(_C_BG))
            err = self._scene_ast.addText("No se pudo construir el AST")
            err.setDefaultTextColor(QColor(_TEXT_MED))

        self._sb.showMessage(
            f"✔ Listo — {len(pasos)-1} paso(s) de derivación por {tipo}")
        self._tabs.setCurrentIndex(0)

    def _on_error(self, msg: str):
        self._set_calculando(False)
        self._sb.showMessage(f"✖ Error: {msg}")
        QMessageBox.critical(self, "Error al generar", msg)

    def _set_calculando(self, activo: bool):
        if activo:
            self._lbl_estado.setText("⏳ Calculando…")
            self._lbl_estado.setStyleSheet(
                f"color:{_ACCENT};font-size:13px;font-weight:bold;")
            self._btn_gen.setEnabled(False)
        else:
            self._lbl_estado.setText("● Listo")
            self._lbl_estado.setStyleSheet(
                "color:#00D4AA;font-size:13px;font-weight:bold;")
            self._btn_gen.setEnabled(True)

    def _limpiar(self):
        self._inp.clear()
        self._txt_pasos.clear()
        self._scene_pt.clear()
        self._scene_pt.setBackgroundBrush(QBrush(_C_BG))
        self._scene_ast.clear()
        self._scene_ast.setBackgroundBrush(QBrush(_C_BG))
        self._sb.showMessage("Limpiado — listo para una nueva expresión")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._scene_pt.items():
            self._view_pt.fitInView(
                self._scene_pt.sceneRect(), Qt.KeepAspectRatio)
        if self._scene_ast.items():
            self._view_ast.fitInView(
                self._scene_ast.sceneRect(), Qt.KeepAspectRatio)


# ══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CFG Tree Generator")
    v = VentanaPrincipal()
    v.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()