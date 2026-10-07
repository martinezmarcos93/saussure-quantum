"""
gui.py — Interfaz gráfica principal de Saussure-Quantum Fusion

Ejecutar desde la raíz del proyecto:
    python gui.py

Requiere que el paquete esté instalado o que saussure_quantum/ esté en el mismo directorio.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import threading
import random

# ── Importar el paquete ───────────────────────────────────────────────────────
try:
    from saussure_quantum import SignoCuanto, Langue
    from saussure_quantum.collapse import (
        colapso_parole, ContextoEnunciativo, medicion_debil
    )
    from saussure_quantum.operators import (
        operador_diferencia, OperadorDiferencia, principio_negatividad
    )
    from saussure_quantum.uncertainty import (
        PrincipioIncertidumbreSaussure, ObservablesSaussureanos, HBAR_SEMIOTICO
    )
    PAQUETE_OK = True
except ImportError as e:
    PAQUETE_OK = False
    IMPORT_ERROR = str(e)


# ── Paleta de colores ─────────────────────────────────────────────────────────
COLORES = {
    "bg":          "#0F0F1A",
    "sidebar":     "#13131F",
    "panel":       "#1A1A2E",
    "borde":       "#2A2A45",
    "acento":      "#7F77DD",
    "acento2":     "#1D9E75",
    "acento3":     "#EF9F27",
    "acento4":     "#D85A30",
    "texto":       "#E8E6F0",
    "texto_sec":   "#8A87A0",
    "entrada":     "#22223A",
    "salida_bg":   "#0D0D18",
    "ok":          "#1D9E75",
    "warn":        "#EF9F27",
    "error":       "#E24B4A",
}

FUENTE_TITULO  = ("Consolas", 13, "bold")
FUENTE_LABEL   = ("Consolas", 10)
FUENTE_MONO    = ("Consolas", 11)
FUENTE_SMALL   = ("Consolas", 9)
FUENTE_SIDEBAR = ("Consolas", 11)
FUENTE_GRANDE  = ("Consolas", 22, "bold")


# ═══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class AppSaussureQuantum(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Saussure–Quantum Fusion  v0.1.0")
        self.minsize(900, 600)
        self.configure(bg=COLORES["bg"])
        self.resizable(True, True)

        # Centrar en pantalla antes de mostrar
        ancho, alto = 1050, 700
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - ancho) // 2
        y = (sh - alto) // 2
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

        self._build_layout()
        self._mostrar_panel("poeta")

        if not PAQUETE_OK:
            self._mostrar_error_importacion()

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = tk.Frame(self, bg=COLORES["sidebar"], width=190)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self._build_sidebar()

        # Separador vertical
        sep = tk.Frame(self, bg=COLORES["borde"], width=1)
        sep.grid(row=0, column=0, sticky="nse")

        # Área principal
        self.main = tk.Frame(self, bg=COLORES["bg"])
        self.main.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)

        # Paneles
        self.paneles = {}
        self.paneles["poeta"]        = PanelPoeta(self.main)
        self.paneles["simulador"]    = PanelSimulador(self.main)
        self.paneles["incertidumbre"]= PanelIncertidumbre(self.main)
        self.paneles["diferencia"]   = PanelDiferencia(self.main)
        self.paneles["teoria"]       = PanelTeoria(self.main)

        for p in self.paneles.values():
            p.grid(row=0, column=0, sticky="nsew")

    def _build_sidebar(self):
        # Logo / título
        tk.Label(
            self.sidebar, text="⟨ψ|", font=("Consolas", 28, "bold"),
            bg=COLORES["sidebar"], fg=COLORES["acento"]
        ).pack(pady=(24, 0))
        tk.Label(
            self.sidebar, text="Saussure\nQuantum", font=("Consolas", 10),
            bg=COLORES["sidebar"], fg=COLORES["texto_sec"], justify="center"
        ).pack(pady=(2, 20))

        sep = tk.Frame(self.sidebar, bg=COLORES["borde"], height=1)
        sep.pack(fill="x", padx=16, pady=(0, 16))

        # Items de navegación
        self.nav_botones = {}
        items = [
            ("poeta",         "◈  Poeta cuántico",   COLORES["acento"]),
            ("simulador",     "◉  Simulador",         COLORES["acento2"]),
            ("incertidumbre", "△  Incertidumbre",     COLORES["acento3"]),
            ("diferencia",    "⊗  Op. Diferencia",    COLORES["acento4"]),
            ("teoria",        "❖  Teoría",            COLORES["texto"]),
        ]
        for key, label, color in items:
            btn = tk.Label(
                self.sidebar, text=label, font=FUENTE_SIDEBAR,
                bg=COLORES["sidebar"], fg=COLORES["texto_sec"],
                anchor="w", padx=20, pady=10, cursor="hand2"
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, k=key: self._mostrar_panel(k))
            btn.bind("<Enter>",    lambda e, b=btn: b.configure(fg=COLORES["texto"]))
            btn.bind("<Leave>",    lambda e, b=btn, k=key: self._hover_leave(b, k))
            self.nav_botones[key] = (btn, color)

        # Versión abajo
        tk.Label(
            self.sidebar, text="v0.1.0", font=FUENTE_SMALL,
            bg=COLORES["sidebar"], fg=COLORES["borde"]
        ).pack(side="bottom", pady=12)

    def _mostrar_panel(self, key):
        self.panel_activo = key
        for k, (btn, color) in self.nav_botones.items():
            if k == key:
                btn.configure(bg=COLORES["panel"], fg=color)
            else:
                btn.configure(bg=COLORES["sidebar"], fg=COLORES["texto_sec"])
        self.paneles[key].tkraise()

    def _hover_leave(self, btn, key):
        if key != self.panel_activo:
            btn.configure(fg=COLORES["texto_sec"])

    def _mostrar_error_importacion(self):
        ventana = tk.Toplevel(self)
        ventana.title("Error de importación")
        ventana.configure(bg=COLORES["bg"])
        ventana.geometry("500x200")
        tk.Label(
            ventana,
            text="No se pudo importar saussure_quantum",
            font=FUENTE_TITULO, bg=COLORES["bg"], fg=COLORES["error"]
        ).pack(pady=20)
        tk.Label(
            ventana, text=IMPORT_ERROR, font=FUENTE_SMALL,
            bg=COLORES["bg"], fg=COLORES["texto_sec"], wraplength=460
        ).pack()
        tk.Label(
            ventana,
            text="Asegurate de que saussure_quantum/ esté en el mismo directorio\n"
                 "o ejecutá: pip install -e .",
            font=FUENTE_SMALL, bg=COLORES["bg"], fg=COLORES["warn"]
        ).pack(pady=16)


# ═══════════════════════════════════════════════════════════════════════════════
#  SISTEMA DE TOOLTIPS
# ═══════════════════════════════════════════════════════════════════════════════

class Tooltip:
    """
    Tooltip que aparece al pasar el mouse sobre un widget.
    Se destruye automáticamente al salir.
    """
    def __init__(self, widget, texto, delay=500):
        self.widget  = widget
        self.texto   = texto
        self.delay   = delay
        self._id     = None
        self._ventana = None
        widget.bind("<Enter>",  self._on_enter)
        widget.bind("<Leave>",  self._on_leave)
        widget.bind("<Button>", self._on_leave)

    def _on_enter(self, event=None):
        self._id = self.widget.after(self.delay, self._mostrar)

    def _on_leave(self, event=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self._ventana:
            self._ventana.destroy()
            self._ventana = None

    def _mostrar(self):
        if self._ventana:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._ventana = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg=COLORES["borde"])
        # Borde exterior
        marco = tk.Frame(tw, bg=COLORES["borde"], padx=1, pady=1)
        marco.pack()
        tk.Label(
            marco, text=self.texto, font=FUENTE_SMALL,
            bg=COLORES["panel"], fg=COLORES["texto"],
            justify="left", wraplength=340, padx=10, pady=8
        ).pack()


# Textos de ayuda por sección y control
AYUDAS = {
    # ── Poeta cuántico ────────────────────────────────────────────────────────
    "poeta_panel": (
        "El Poeta cuántico genera versos usando colapsos probabilísticos.\n"
        "Cada palabra comienza en superposición de significados posibles\n"
        "y 'colapsa' al ser pronunciada, igual que un estado cuántico\n"
        "colapsa al ser medido. El resultado es poesía no determinista."
    ),
    "poeta_versos": (
        "Cantidad de versos del poema.\n"
        "Cada verso usa una estructura gramatical aleatoria\n"
        "(sustantivo-verbo-adjetivo, etc.)."
    ),
    "poeta_temp": (
        "Temperatura semántica (análoga a la temperatura en física estadística).\n"
        "Baja (1.0): el sistema colapsa hacia las palabras más probables → versos más predecibles.\n"
        "Alta (3.0): distribuye la probabilidad más uniformemente → versos más sorprendentes."
    ),
    "poeta_modo": (
        "Normal: temperatura tal como se configura.\n"
        "Caótico: temperatura multiplicada × 2.5 → máxima aleatoriedad.\n"
        "Mínima incertidumbre: temperatura fija 0.3 → versos más coherentes y repetitivos."
    ),
    # ── Simulador ─────────────────────────────────────────────────────────────
    "sim_panel": (
        "El Simulador explora la relación de incertidumbre de Robertson:\n\n"
        "  ΔS · ΔP ≥ ½|⟨[S,P]⟩|\n\n"
        "La cota depende del estado. En dimensión finita NO existe la cota\n"
        "universal ℏ/2: un estado base tiene ΔS=0, ΔP=ℏ/√2 y producto 0.\n\n"
        "ΔS = incertidumbre sintagmática (¿dónde aparece el signo en la frase?)\n"
        "ΔP = incertidumbre paradigmática (¿con qué otras palabras puede sustituirse?)\n\n"
        "Es una analogía formal con posición-momento, no una equivalencia física\n"
        "ni una ley empírica del lenguaje."
    ),
    "sim_tipo": (
        "Sintagmático puro: posición exacta en la frase → ΔS=0, ΔP=ℏ/√2 (finita).\n"
        "Paradigmático puro: onda plana → ΔP=0, ΔS=√((d²−1)/12).\n"
        "Mínima incertidumbre: nombre histórico de un estado gaussiano de referencia;\n"
        "  no minimiza el producto ΔS·ΔP.\n"
        "Superposición uniforme: es la onda plana de modo 0 → ΔP=0 (paradigma definido)."
    ),
    "sim_dim": (
        "Dimensión del espacio lingüístico (cantidad de términos en el sistema).\n"
        "Más dimensión = sistema más complejo = incertidumbres más grandes."
    ),
    "sim_pos": (
        "Para estado sintagmático: índice de la posición en la frase (0 = primera).\n"
        "Para estado paradigmático: índice del modo de sustitución."
    ),
    # ── Incertidumbre ─────────────────────────────────────────────────────────
    "inc_panel": (
        "Analizá el principio de incertidumbre sobre tu propio conjunto de signos.\n\n"
        "Ingresá los significantes (palabras, fonemas, conceptos) separados por coma\n"
        "y sus amplitudes (números que representan el 'peso' de cada uno).\n"
        "Las amplitudes se normalizan automáticamente.\n\n"
        "Ejemplos de uso:\n"
        "  • Fonemas:   /p/, /b/, /t/  →  amplitudes: 1, 0.5, 0.3\n"
        "  • Animales:  perro, gato, pez  →  amplitudes: 1, 1, 1\n"
        "  • Conceptos: verdad, mentira, duda  →  amplitudes: 2, 1, 0.5"
    ),
    "inc_sigs": (
        "Lista de significantes separados por coma.\n"
        "Pueden ser palabras, fonemas, símbolos o cualquier unidad lingüística.\n"
        "Ejemplos: 'sol, luna, estrella'  |  '/p/, /b/, /t/'  |  'amor, odio, indiferencia'"
    ),
    "inc_amps": (
        "Amplitudes de probabilidad para cada significante (en el mismo orden).\n"
        "No necesitan sumar 1 — se normalizan automáticamente.\n"
        "Mayor amplitud = mayor probabilidad de colapso a ese significante.\n"
        "Ejemplo: '1, 0.5, 0.3' hace que el primero sea el más probable."
    ),
    "inc_paradoja": (
        "La paradoja del observador muestra que medir un eje perturba el otro.\n"
        "Medir el sintagma (posición) aumenta la incertidumbre paradigmática,\n"
        "y medir el paradigma (sustitución) aumenta la sintagmática.\n"
        "No hay observación sin perturbación — igual que en mecánica cuántica."
    ),
    # ── Operador diferencia ───────────────────────────────────────────────────
    "op_panel": (
        "El Operador Diferencia D̂ materializa el principio central de Saussure:\n\n"
        "  'En la lengua solo hay diferencias sin términos positivos'\n\n"
        "Un signo no tiene significado por sí mismo, sino por oponerse a todos\n"
        "los demás signos del sistema. /p/ ES porque NO ES /b/ ni /t/.\n\n"
        "D̂ transforma estados 'sustanciales' (un signo aislado) en estados\n"
        "'diferenciales' (un signo como red de oposiciones).\n\n"
        "Ingresá los signos del sistema, uno por línea."
    ),
    "op_signos": (
        "Ingresá los signos del sistema lingüístico, uno por línea.\n"
        "El operador diferencia los tomará como un sistema de oposiciones.\n\n"
        "Ejemplos:\n"
        "  Fonemas:   /p/  /b/  /t/\n"
        "  Colores:   rojo  verde  azul  amarillo\n"
        "  Conceptos: vida  muerte  sueño  realidad\n"
        "  Animales:  perro  gato  ratón"
    ),
    "op_negatividad": (
        "El análisis de negatividad muestra cuánto 'debe' cada signo a no ser los otros.\n"
        "Un signo con alta negatividad es muy dependiente del contraste con el resto.\n"
        "Esto es la fuerza diferencial de Saussure cuantificada."
    ),
    "op_similitud": (
        "La similitud diferencial mide qué tan parecidos son dos signos\n"
        "en términos de sus diferencias con los demás, no de su 'sustancia'.\n"
        "1.0 = idénticos en su red de oposiciones.\n"
        "0.0 = completamente ortogonales en el sistema."
    ),
}


def agregar_tooltip(widget, clave):
    """Agrega un tooltip a un widget usando la clave en AYUDAS."""
    if clave in AYUDAS:
        Tooltip(widget, AYUDAS[clave])


# ═══════════════════════════════════════════════════════════════════════════════
#  WIDGETS REUTILIZABLES
# ═══════════════════════════════════════════════════════════════════════════════

def label_titulo(parent, texto, color=None):
    return tk.Label(
        parent, text=texto, font=FUENTE_TITULO,
        bg=COLORES["bg"], fg=color or COLORES["texto"], anchor="w"
    )

def label_sec(parent, texto):
    return tk.Label(
        parent, text=texto, font=FUENTE_LABEL,
        bg=COLORES["bg"], fg=COLORES["texto_sec"], anchor="w"
    )

def seccion(parent, titulo, color):
    f = tk.Frame(parent, bg=COLORES["panel"],
                 highlightbackground=COLORES["borde"], highlightthickness=1)
    tk.Label(f, text=titulo, font=FUENTE_SMALL, bg=COLORES["panel"],
             fg=color, anchor="w", padx=10, pady=6).pack(fill="x")
    tk.Frame(f, bg=COLORES["borde"], height=1).pack(fill="x")
    return f

def area_salida(parent, height=8):
    txt = scrolledtext.ScrolledText(
        parent, height=height, font=FUENTE_MONO,
        bg=COLORES["salida_bg"], fg=COLORES["texto"],
        insertbackground=COLORES["acento"],
        selectbackground=COLORES["acento"],
        relief="flat", borderwidth=0, wrap="word",
        state="disabled"
    )
    return txt

def escribir_salida(widget, texto, limpiar=True):
    widget.configure(state="normal")
    if limpiar:
        widget.delete("1.0", "end")
    widget.insert("end", texto)
    widget.see("end")
    widget.configure(state="disabled")

def boton(parent, texto, comando, color=None):
    c = color or COLORES["acento"]
    btn = tk.Label(
        parent, text=texto, font=FUENTE_LABEL,
        bg=c, fg=COLORES["bg"],
        padx=14, pady=7, cursor="hand2",
        relief="flat"
    )
    btn.bind("<Button-1>", lambda e: comando())
    btn.bind("<Enter>",    lambda e: btn.configure(bg=_aclarar(c)))
    btn.bind("<Leave>",    lambda e: btn.configure(bg=c))
    return btn

def slider_con_label(parent, texto, desde, hasta, valor_ini, paso=1, fmt="{:.0f}"):
    fila = tk.Frame(parent, bg=COLORES["panel"])
    tk.Label(fila, text=texto, font=FUENTE_LABEL, bg=COLORES["panel"],
             fg=COLORES["texto_sec"], width=18, anchor="w").pack(side="left", padx=(10,0))
    var = tk.DoubleVar(value=valor_ini)
    lbl_val = tk.Label(fila, text=fmt.format(valor_ini), font=FUENTE_LABEL,
                       bg=COLORES["panel"], fg=COLORES["texto"], width=6, anchor="e")
    lbl_val.pack(side="right", padx=10)
    sl = ttk.Scale(fila, from_=desde, to=hasta, variable=var, orient="horizontal")
    sl.pack(side="left", fill="x", expand=True, padx=8)
    def _actualizar(*_):
        lbl_val.configure(text=fmt.format(var.get()))
    var.trace_add("write", _actualizar)
    return fila, var

def _aclarar(hex_color):
    r = min(255, int(hex_color[1:3], 16) + 30)
    g = min(255, int(hex_color[3:5], 16) + 30)
    b = min(255, int(hex_color[5:7], 16) + 30)
    return f"#{r:02x}{g:02x}{b:02x}"

def metric_card(parent, label, var_texto, color):
    f = tk.Frame(parent, bg=COLORES["panel"],
                 highlightbackground=COLORES["borde"], highlightthickness=1)
    tk.Label(f, text=label, font=FUENTE_SMALL, bg=COLORES["panel"],
             fg=COLORES["texto_sec"]).pack(pady=(8,0))
    tk.Label(f, textvariable=var_texto, font=FUENTE_GRANDE,
             bg=COLORES["panel"], fg=color).pack(pady=(0,8))
    return f


# ═══════════════════════════════════════════════════════════════════════════════
#  PANEL 1 — POETA CUÁNTICO
# ═══════════════════════════════════════════════════════════════════════════════

class PanelPoeta(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._build()

    def _build(self):
        # Cabecera
        cab = tk.Frame(self, bg=COLORES["bg"])
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(24,0))
        tit = label_titulo(cab, "◈  Poeta cuántico", COLORES["acento"])
        tit.pack(anchor="w")
        agregar_tooltip(tit, "poeta_panel")
        desc = label_sec(cab, "Genera versos por colapso de superposiciones semánticas  (?)")
        desc.pack(anchor="w", pady=(2,0))
        agregar_tooltip(desc, "poeta_panel")

        # Controles
        ctrl = seccion(self, "PARÁMETROS", COLORES["acento"])
        ctrl.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        fila1, self.var_versos = slider_con_label(ctrl, "Versos", 1, 8, 4)
        fila1.pack(fill="x", pady=4)
        agregar_tooltip(fila1, "poeta_versos")
        fila2, self.var_temp = slider_con_label(ctrl, "Temperatura ℏ", 1, 30, 10,
                                                 fmt="{:.1f}")
        fila2.pack(fill="x", pady=4)
        agregar_tooltip(fila2, "poeta_temp")

        fila_modo = tk.Frame(ctrl, bg=COLORES["panel"])
        tk.Label(fila_modo, text="Modo", font=FUENTE_LABEL, bg=COLORES["panel"],
                 fg=COLORES["texto_sec"], width=18, anchor="w").pack(side="left", padx=(10,0))
        self.var_modo = tk.StringVar(value="Normal")
        combo = ttk.Combobox(fila_modo, textvariable=self.var_modo,
                             values=["Normal", "Caótico", "Mínima incertidumbre"],
                             state="readonly", font=FUENTE_LABEL, width=22)
        combo.pack(side="left", padx=8, pady=6)
        agregar_tooltip(fila_modo, "poeta_modo")
        fila_modo.pack(fill="x", pady=4)

        # Diccionario personalizable
        dic_sec = seccion(self, "DICCIONARIO  (palabras separadas por coma)", COLORES["acento"])
        dic_sec.grid(row=2, column=0, sticky="ew", padx=24, pady=(0,4))

        DEFAULTS = {
            "Sustantivos": "amor, caos, luz, sombra, infinito, vacío, tiempo, silencio",
            "Verbos":      "nace, muere, sueña, vuela, cae, asciende, persiste, colapsa",
            "Adjetivos":   "eterno, fugaz, profundo, ligero, oscuro, brillante, quantum, discreto",
            "Conectores":  "y, pero, cuando, donde, como, mientras, porque, aunque",
        }
        self.dic_entries = {}
        for cat, default in DEFAULTS.items():
            fila = tk.Frame(dic_sec, bg=COLORES["panel"])
            tk.Label(fila, text=cat, font=FUENTE_LABEL, bg=COLORES["panel"],
                     fg=COLORES["texto_sec"], width=12, anchor="w").pack(side="left", padx=(10,0))
            entry = tk.Entry(fila, font=FUENTE_LABEL, bg=COLORES["entrada"],
                             fg=COLORES["texto"], insertbackground=COLORES["acento"],
                             relief="flat")
            entry.insert(0, default)
            entry.pack(side="left", fill="x", expand=True, padx=8, pady=4)
            fila.pack(fill="x", pady=2)
            self.dic_entries[cat.lower()] = entry

        # Botones
        btn_row = tk.Frame(self, bg=COLORES["bg"])
        btn_row.grid(row=3, column=0, sticky="nw", padx=24, pady=(4,8))
        boton(btn_row, "  Generar poema  ", self._generar,
              COLORES["acento"]).pack(side="left", padx=(0,8))
        boton(btn_row, "  Exportar .txt  ", self._exportar,
              COLORES["acento2"]).pack(side="left", padx=(0,8))
        boton(btn_row, "  Restaurar diccionario  ", self._restaurar_dic,
              COLORES["borde"]).pack(side="left", padx=(0,8))
        boton(btn_row, "  Limpiar  ", self._limpiar,
              COLORES["borde"]).pack(side="left")

        # Salida
        sal = seccion(self, "POEMA GENERADO", COLORES["acento"])
        sal.grid(row=4, column=0, sticky="nsew", padx=24, pady=(0,8))
        self.rowconfigure(4, weight=1)
        self.salida = area_salida(sal, height=7)
        self.salida.pack(fill="both", expand=True, padx=10, pady=10)

        # Métricas
        met_frame = tk.Frame(self, bg=COLORES["bg"])
        met_frame.grid(row=5, column=0, sticky="ew", padx=24, pady=(0,20))
        for i in range(3):
            met_frame.columnconfigure(i, weight=1)
        self.m_palabras = tk.StringVar(value="—")
        self.m_colapsos = tk.StringVar(value="—")
        self.m_entropia = tk.StringVar(value="—")
        metric_card(met_frame, "Palabras", self.m_palabras, COLORES["acento"]).grid(
            row=0, column=0, sticky="ew", padx=(0,6))
        metric_card(met_frame, "Colapsos", self.m_colapsos, COLORES["acento2"]).grid(
            row=0, column=1, sticky="ew", padx=3)
        metric_card(met_frame, "Entropía media", self.m_entropia, COLORES["acento3"]).grid(
            row=0, column=2, sticky="ew", padx=(6,0))

    def _parse_dic(self):
        """Leer el diccionario personalizado desde los campos de texto."""
        dic = {}
        for cat, entry in self.dic_entries.items():
            palabras = [p.strip() for p in entry.get().split(",") if p.strip()]
            if len(palabras) < 2:
                raise ValueError(f"'{cat}' necesita al menos 2 palabras")
            amps = [1.0] * len(palabras)
            dic[cat] = SignoCuanto(palabras, amps)
        return dic

    def _exportar(self):
        """Guardar el poema actual en un archivo .txt con metadatos."""
        contenido = self.salida.get("1.0", "end").strip()
        if not contenido:
            escribir_salida(self.salida, "⚠  No hay poema para exportar. Generá uno primero.\n")
            return

        from tkinter import filedialog
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_default = f"poema_cuantico_{timestamp}.txt"

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=nombre_default,
            title="Guardar poema"
        )
        if not ruta:
            return  # Usuario canceló

        modo     = self.var_modo.get()
        versos   = int(self.var_versos.get())
        temp     = self.var_temp.get() / 10.0
        palabras = self.m_palabras.get()
        entropia = self.m_entropia.get()

        encabezado = (
            f"╔══════════════════════════════════════════╗\n"
            f"║      POEMA CUÁNTICO — Saussure×Quantum   ║\n"
            f"╚══════════════════════════════════════════╝\n"
            f"\n"
            f"Generado:        {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Versos:          {versos}\n"
            f"Modo:            {modo}\n"
            f"Temperatura ℏ:  {temp:.1f}\n"
            f"Palabras:        {palabras}\n"
            f"Entropía media: {entropia}\n"
            f"\n{'─'*44}\n\n"
        )

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(encabezado + contenido + "\n")

        # Confirmación en la zona de salida
        escribir_salida(
            self.salida,
            contenido + f"\n\n✅  Poema exportado a:\n   {ruta}",
            limpiar=True
        )

    def _restaurar_dic(self):
        """Restaurar el diccionario a los valores por defecto."""
        defaults = {
            "sustantivos": "amor, caos, luz, sombra, infinito, vacío, tiempo, silencio",
            "verbos":      "nace, muere, sueña, vuela, cae, asciende, persiste, colapsa",
            "adjetivos":   "eterno, fugaz, profundo, ligero, oscuro, brillante, quantum, discreto",
            "conectores":  "y, pero, cuando, donde, como, mientras, porque, aunque",
        }
        for cat, entry in self.dic_entries.items():
            entry.delete(0, "end")
            entry.insert(0, defaults[cat])

    def _generar(self):
        if not PAQUETE_OK:
            escribir_salida(self.salida, "⚠  Error: paquete no disponible.\n")
            return

        try:
            diccionario = self._parse_dic()
        except ValueError as e:
            escribir_salida(self.salida, f"⚠  Error en diccionario: {e}\n")
            return

        n_versos = int(self.var_versos.get())
        temp_raw = self.var_temp.get() / 10.0
        modo     = self.var_modo.get()

        if modo == "Caótico":
            humor = temp_raw * 2.5
        elif modo == "Mínima incertidumbre":
            humor = 0.3
        else:
            humor = temp_raw

        cats = list(diccionario.keys())
        estructuras = [
            [cats[0], cats[1], cats[2]] if len(cats) >= 3 else cats,
            [cats[2], cats[0], cats[1]] if len(cats) >= 3 else cats,
            [cats[1], cats[0]]          if len(cats) >= 2 else cats,
            [cats[3], cats[2], cats[0], cats[1]] if len(cats) >= 4 else cats,
        ]

        import copy
        versos = []
        total_entropia = []
        colapsos = 0

        for _ in range(n_versos):
            h = humor * (0.8 + 0.4 * np.sin(len(versos)))
            ctx_v = ContextoEnunciativo(temperatura_semantica=h)
            estructura = random.choice(estructuras)
            palabras = []
            for cat in estructura:
                signo = copy.deepcopy(diccionario[cat])
                probs = np.abs(signo.amplitudes) ** 2
                ent = -np.sum(probs * np.log(probs + 1e-10))
                total_entropia.append(ent)
                palabra, _, _ = colapso_parole(signo, ctx_v)
                palabras.append(palabra)
                colapsos += 1
            verso = " ".join(palabras)
            verso = verso[0].upper() + verso[1:]
            versos.append(verso)

        poema = "\n".join(versos)
        palabras_total = sum(len(v.split()) for v in versos)
        entropia_media = np.mean(total_entropia) if total_entropia else 0

        escribir_salida(self.salida, poema)
        self.m_palabras.set(str(palabras_total))
        self.m_colapsos.set(str(colapsos))
        self.m_entropia.set(f"{entropia_media:.2f}")

    def _limpiar(self):
        escribir_salida(self.salida, "")
        self.m_palabras.set("—")
        self.m_colapsos.set("—")
        self.m_entropia.set("—")


# ═══════════════════════════════════════════════════════════════════════════════
#  PANEL 2 — SIMULADOR DE INCERTIDUMBRE
# ═══════════════════════════════════════════════════════════════════════════════

class PanelSimulador(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._build()

    def _build(self):
        cab = tk.Frame(self, bg=COLORES["bg"])
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(24,0))
        tit = label_titulo(cab, "◉  Simulador de incertidumbre", COLORES["acento2"])
        tit.pack(anchor="w")
        agregar_tooltip(tit, "sim_panel")
        desc = label_sec(cab, "Explora la cota de Robertson ΔS·ΔP ≥ ½|⟨[S,P]⟩| en estados lingüísticos  (?)")
        desc.pack(anchor="w", pady=(2,0))
        agregar_tooltip(desc, "sim_panel")

        ctrl = seccion(self, "CONFIGURACIÓN", COLORES["acento2"])
        ctrl.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        fila_tipo = tk.Frame(ctrl, bg=COLORES["panel"])
        tk.Label(fila_tipo, text="Tipo de estado", font=FUENTE_LABEL,
                 bg=COLORES["panel"], fg=COLORES["texto_sec"],
                 width=18, anchor="w").pack(side="left", padx=(10,0))
        self.var_tipo = tk.StringVar(value="Sintagmático puro")
        combo = ttk.Combobox(fila_tipo, textvariable=self.var_tipo,
                             values=["Sintagmático puro", "Paradigmático puro",
                                     "Mínima incertidumbre", "Superposición uniforme"],
                             state="readonly", font=FUENTE_LABEL, width=26)
        combo.pack(side="left", padx=8, pady=6)
        agregar_tooltip(fila_tipo, "sim_tipo")
        fila_tipo.pack(fill="x", pady=4)

        fila_dim, self.var_dim = slider_con_label(ctrl, "Dimensión", 4, 32, 20)
        fila_dim.pack(fill="x", pady=4)
        agregar_tooltip(fila_dim, "sim_dim")
        fila_pos, self.var_pos = slider_con_label(ctrl, "Posición / Modo", 0, 19, 5)
        fila_pos.pack(fill="x", pady=4)
        agregar_tooltip(fila_pos, "sim_pos")

        btn_row = tk.Frame(self, bg=COLORES["bg"])
        btn_row.grid(row=2, column=0, sticky="nw", padx=24, pady=(0,8))
        boton(btn_row, "  Analizar estado  ", self._analizar,
              COLORES["acento2"]).pack(side="left", padx=(0,8))
        boton(btn_row, "  Demostrar principio  ", self._demostrar,
              COLORES["borde"]).pack(side="left", padx=(0,8))
        boton(btn_row, "  Comparar 4 estados  ", self._comparar,
              COLORES["borde"]).pack(side="left")

        sal = seccion(self, "ANÁLISIS DE INCERTIDUMBRE", COLORES["acento2"])
        sal.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0,8))
        self.rowconfigure(3, weight=1)
        self.salida = area_salida(sal, height=10)
        self.salida.pack(fill="both", expand=True, padx=10, pady=10)

        met_frame = tk.Frame(self, bg=COLORES["bg"])
        met_frame.grid(row=4, column=0, sticky="ew", padx=24, pady=(0,20))
        for i in range(3):
            met_frame.columnconfigure(i, weight=1)
        self.m_ds   = tk.StringVar(value="—")
        self.m_dp   = tk.StringVar(value="—")
        self.m_prod = tk.StringVar(value="—")
        metric_card(met_frame, "ΔS (sintagma)", self.m_ds, COLORES["acento2"]).grid(
            row=0, column=0, sticky="ew", padx=(0,6))
        metric_card(met_frame, "ΔP (paradigma)", self.m_dp, COLORES["acento3"]).grid(
            row=0, column=1, sticky="ew", padx=3)
        metric_card(met_frame, "ΔS·ΔP", self.m_prod, COLORES["acento4"]).grid(
            row=0, column=2, sticky="ew", padx=(6,0))

    def _get_estado(self):
        dim  = int(self.var_dim.get())
        pos  = int(min(self.var_pos.get(), dim - 1))
        lang = Langue(dim)
        principio = PrincipioIncertidumbreSaussure(lang)
        tipo = self.var_tipo.get()
        if tipo == "Sintagmático puro":
            return principio.estado_sintagmatico_puro(pos), principio
        elif tipo == "Paradigmático puro":
            return principio.estado_paradigmatico_puro(pos), principio
        elif tipo == "Mínima incertidumbre":
            return principio.obs.estado_minima_incertidumbre(), principio
        else:
            return lang.superposicion([1] * dim), principio

    def _analizar(self):
        if not PAQUETE_OK:
            return
        estado, principio = self._get_estado()
        analisis = principio.analizar_estado(estado)
        dS   = analisis["delta_sintagma"]
        dP   = analisis["delta_paradigma"]
        prod = analisis["producto_incertidumbre"]
        cota = analisis["cota_robertson"]

        satisface = "✓ SÍ" if analisis["satisface_robertson"] else "✗ NO"
        txt = (
            f"Estado:           {self.var_tipo.get()}\n"
            f"Dimensión:        {int(self.var_dim.get())}\n\n"
            f"ΔS (sintagma):    {dS:.6f}\n"
            f"ΔP (paradigma):   {dP:.6f}\n"
            f"ΔS · ΔP:          {prod:.6f}\n"
            f"Cota Robertson:   {cota:.6f}\n"
            f"Factor s/ cota:   {analisis['factor_sobre_cota']:.2f}x\n\n"
            f"Satisface ΔS·ΔP ≥ ½|⟨[S,P]⟩|:  {satisface}\n\n"
            f"Interpretación:\n  {analisis['interpretacion']}\n\n"
            f"Dominancia:\n  {analisis['dominancia']}\n"
        )
        escribir_salida(self.salida, txt)
        self.m_ds.set(f"{dS:.3f}")
        self.m_dp.set(f"{dP:.3f}")
        self.m_prod.set(f"{prod:.3f}")

    def _demostrar(self):
        if not PAQUETE_OK:
            return
        dim = int(self.var_dim.get())
        lang = Langue(dim)
        principio = PrincipioIncertidumbreSaussure(lang)
        demo = principio.demostrar_principio()

        lineas = ["╔═══════════════════════════════════════╗",
                  "║   ESTADOS DE REFERENCIA                ║",
                  "║   ΔS · ΔP ≥ ½|⟨[S,P]⟩|  (Robertson)   ║",
                  "╚═══════════════════════════════════════╝\n"]
        for nombre, datos in demo.items():
            lineas.append(f"[ {nombre.upper()} ]")
            lineas.append(f"  ΔS = {datos['delta_sintagma']:.4f}")
            lineas.append(f"  ΔP = {datos['delta_paradigma']:.4f}")
            lineas.append(f"  ΔS·ΔP = {datos['producto']:.4f}   (cota Robertson = {datos['cota_robertson']:.4f})\n")

        lineas.append("La cota depende del estado: en los dos estados puros vale 0")
        lineas.append("y el producto también. No hay cota universal ℏ/2 en dimensión finita.")
        escribir_salida(self.salida, "\n".join(lineas))

    def _comparar(self):
        """Tabla comparativa de los 4 tipos de estado en la dimensión actual."""
        if not PAQUETE_OK:
            return
        dim = int(self.var_dim.get())
        pos = int(min(self.var_pos.get(), dim - 1))
        lang = Langue(dim)
        principio = PrincipioIncertidumbreSaussure(lang)

        tipos = [
            ("Sintagmático puro",    principio.estado_sintagmatico_puro(pos)),
            ("Paradigmático puro",   principio.estado_paradigmatico_puro(pos)),
            ("Mínima incertidumbre", principio.obs.estado_minima_incertidumbre()),
            ("Superposición uniforme", lang.superposicion([1] * dim)),
        ]

        sep  = "─" * 62
        col  = f"{'TIPO DE ESTADO':<24} {'ΔS':>8} {'ΔP':>8} {'ΔS·ΔP':>10} {'Factor':>7}"
        lineas = [
            "╔══════════════════════════════════════════════════════════╗",
            f"║  COMPARACIÓN DE ESTADOS  —  dim={dim:<3}  pos/modo={pos:<3}        ║",
            "╚══════════════════════════════════════════════════════════╝\n",
            col,
            sep,
        ]

        for nombre, estado in tipos:
            a = principio.analizar_estado(estado)
            dS   = a["delta_sintagma"]
            dP   = a["delta_paradigma"]
            prod = a["producto_incertidumbre"]
            factor = a["factor_sobre_cota"]
            ok = "✓" if a["satisface_robertson"] else "✗"
            # Limitar valores infinitos para display
            dS_s   = f"{dS:.4f}"   if np.isfinite(dS)   else "  ∞"
            dP_s   = f"{dP:.4f}"   if np.isfinite(dP)   else "  ∞"
            prod_s = f"{prod:.4f}" if np.isfinite(prod)  else "    ∞"
            fac_s  = f"{factor:.2f}x" if np.isfinite(factor) else "   ∞x"
            lineas.append(f"{ok} {nombre:<23} {dS_s:>8} {dP_s:>8} {prod_s:>10} {fac_s:>7}")

        lineas += [
            sep,
            "  ✓ = satisface Robertson (ΔS·ΔP ≥ ½|⟨[S,P]⟩|)   ✗ = lo viola\n",
            "  Factor = ΔS·ΔP / cota de Robertson del propio estado (∞ si la cota es 0).",
            "  La cota depende del estado; no existe un mínimo universal ℏ/2.",
        ]
        escribir_salida(self.salida, "\n".join(lineas))
        # Actualizar métricas con el tipo seleccionado actualmente
        estado_actual, _ = self._get_estado()
        a = principio.analizar_estado(estado_actual)
        self.m_ds.set(f"{a['delta_sintagma']:.3f}"   if np.isfinite(a['delta_sintagma'])   else "∞")
        self.m_dp.set(f"{a['delta_paradigma']:.3f}"  if np.isfinite(a['delta_paradigma'])  else "∞")
        self.m_prod.set(f"{a['producto_incertidumbre']:.3f}" if np.isfinite(a['producto_incertidumbre']) else "∞")


# ═══════════════════════════════════════════════════════════════════════════════
#  PANEL 3 — PRINCIPIO DE INCERTIDUMBRE (análisis detallado)
# ═══════════════════════════════════════════════════════════════════════════════

class PanelIncertidumbre(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._build()

    def _build(self):
        cab = tk.Frame(self, bg=COLORES["bg"])
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(24,0))
        tit = label_titulo(cab, "△  Principio de incertidumbre", COLORES["acento3"])
        tit.pack(anchor="w")
        agregar_tooltip(tit, "inc_panel")
        desc = label_sec(cab, "Análisis de incertidumbre y paradoja del observador  (?)")
        desc.pack(anchor="w", pady=(2,0))
        agregar_tooltip(desc, "inc_panel")

        ctrl = seccion(self, "ESTADO PERSONALIZADO", COLORES["acento3"])
        ctrl.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        fila_sigs = tk.Frame(ctrl, bg=COLORES["panel"])
        lbl_sigs = tk.Label(fila_sigs, text="Significantes  (?)", font=FUENTE_LABEL,
                 bg=COLORES["panel"], fg=COLORES["texto_sec"],
                 width=18, anchor="w")
        lbl_sigs.pack(side="left", padx=(10,0))
        agregar_tooltip(lbl_sigs, "inc_sigs")
        self.entry_sigs = tk.Entry(fila_sigs, font=FUENTE_LABEL,
                                   bg=COLORES["entrada"], fg=COLORES["texto"],
                                   insertbackground=COLORES["acento3"],
                                   relief="flat", width=32)
        self.entry_sigs.insert(0, "perro, gato, ratón, pájaro")
        self.entry_sigs.pack(side="left", padx=8, pady=6)
        agregar_tooltip(self.entry_sigs, "inc_sigs")
        fila_sigs.pack(fill="x", pady=4)

        fila_amps = tk.Frame(ctrl, bg=COLORES["panel"])
        lbl_amps = tk.Label(fila_amps, text="Amplitudes  (?)", font=FUENTE_LABEL,
                 bg=COLORES["panel"], fg=COLORES["texto_sec"],
                 width=18, anchor="w")
        lbl_amps.pack(side="left", padx=(10,0))
        agregar_tooltip(lbl_amps, "inc_amps")
        self.entry_amps = tk.Entry(fila_amps, font=FUENTE_LABEL,
                                   bg=COLORES["entrada"], fg=COLORES["texto"],
                                   insertbackground=COLORES["acento3"],
                                   relief="flat", width=32)
        self.entry_amps.insert(0, "1, 0.5, 0.3, 0.8")
        self.entry_amps.pack(side="left", padx=8, pady=6)
        agregar_tooltip(self.entry_amps, "inc_amps")
        fila_amps.pack(fill="x", pady=4)

        # Ejemplos predefinidos
        fila_ej = tk.Frame(ctrl, bg=COLORES["panel"])
        tk.Label(fila_ej, text="Cargar ejemplo", font=FUENTE_LABEL,
                 bg=COLORES["panel"], fg=COLORES["texto_sec"],
                 width=18, anchor="w").pack(side="left", padx=(10,0))
        self.var_ejemplo = tk.StringVar(value="— elegir —")
        ejemplos = [
            "— elegir —",
            "Fonemas: /p/ /b/ /t/",
            "Animales: perro gato ratón",
            "Colores: rojo verde azul amarillo",
            "Filosofía: verdad mentira duda certeza",
            "Tiempo: pasado presente futuro",
            "Emociones: amor odio miedo alegría tristeza",
            "Planetas: Mercurio Venus Tierra Marte Júpiter",
        ]
        combo_ej = ttk.Combobox(fila_ej, textvariable=self.var_ejemplo,
                                values=ejemplos, state="readonly",
                                font=FUENTE_LABEL, width=30)
        combo_ej.pack(side="left", padx=8, pady=6)
        combo_ej.bind("<<ComboboxSelected>>", self._cargar_ejemplo)
        fila_ej.pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=COLORES["bg"])
        btn_row.grid(row=2, column=0, sticky="nw", padx=24, pady=(0,8))
        boton(btn_row, "  Calcular incertidumbre  ", self._calcular,
              COLORES["acento3"]).pack(side="left", padx=(0,8))
        btn_p = boton(btn_row, "  Paradoja del observador  ", self._paradoja,
              COLORES["borde"])
        btn_p.pack(side="left")
        agregar_tooltip(btn_p, "inc_paradoja")

        sal = seccion(self, "RESULTADO", COLORES["acento3"])
        sal.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0,8))
        self.rowconfigure(3, weight=1)
        self.salida = area_salida(sal, height=12)
        self.salida.pack(fill="both", expand=True, padx=10, pady=10)

        met_frame = tk.Frame(self, bg=COLORES["bg"])
        met_frame.grid(row=4, column=0, sticky="ew", padx=24, pady=(0,20))
        for i in range(3):
            met_frame.columnconfigure(i, weight=1)
        self.m_ds    = tk.StringVar(value="—")
        self.m_dp    = tk.StringVar(value="—")
        self.m_ok    = tk.StringVar(value="—")
        metric_card(met_frame, "ΔS", self.m_ds, COLORES["acento3"]).grid(
            row=0, column=0, sticky="ew", padx=(0,6))
        metric_card(met_frame, "ΔP", self.m_dp, COLORES["acento3"]).grid(
            row=0, column=1, sticky="ew", padx=3)
        metric_card(met_frame, "Principio", self.m_ok, COLORES["acento2"]).grid(
            row=0, column=2, sticky="ew", padx=(6,0))

    def _cargar_ejemplo(self, event=None):
        """Carga un ejemplo predefinido en los campos de significantes y amplitudes."""
        EJEMPLOS = {
            "Fonemas: /p/ /b/ /t/":              ("/p/, /b/, /t/",              "1, 0.8, 0.6"),
            "Animales: perro gato ratón":         ("perro, gato, ratón",         "1, 0.7, 0.4"),
            "Colores: rojo verde azul amarillo":  ("rojo, verde, azul, amarillo","1, 1, 1, 1"),
            "Filosofía: verdad mentira duda certeza": (
                "verdad, mentira, duda, certeza", "1.5, 0.8, 0.5, 1.2"),
            "Tiempo: pasado presente futuro":     ("pasado, presente, futuro",   "0.6, 1.5, 0.9"),
            "Emociones: amor odio miedo alegría tristeza": (
                "amor, odio, miedo, alegría, tristeza", "1.2, 0.7, 0.5, 1.0, 0.6"),
            "Planetas: Mercurio Venus Tierra Marte Júpiter": (
                "Mercurio, Venus, Tierra, Marte, Júpiter", "0.4, 0.7, 1.5, 0.9, 1.1"),
        }
        seleccion = self.var_ejemplo.get()
        if seleccion in EJEMPLOS:
            sigs, amps = EJEMPLOS[seleccion]
            self.entry_sigs.delete(0, "end")
            self.entry_sigs.insert(0, sigs)
            self.entry_amps.delete(0, "end")
            self.entry_amps.insert(0, amps)

    def _parse_estado(self):
        sigs_txt = self.entry_sigs.get()
        amps_txt = self.entry_amps.get()
        sigs = [s.strip() for s in sigs_txt.split(",")]
        amps = [float(a.strip()) for a in amps_txt.split(",")]
        if len(sigs) != len(amps):
            raise ValueError(f"Cantidad distinta: {len(sigs)} significantes, {len(amps)} amplitudes")
        return SignoCuanto(sigs, amps)

    def _calcular(self):
        if not PAQUETE_OK:
            return
        try:
            estado = self._parse_estado()
        except Exception as e:
            escribir_salida(self.salida, f"Error de entrada: {e}\n")
            return

        from saussure_quantum.uncertainty import incertidumbre_saussure_heisenberg
        res = incertidumbre_saussure_heisenberg(estado)
        dS   = res["delta_sintagma"]
        dP   = res["delta_paradigma"]
        prod = res["producto_incertidumbre"]
        cota = res["cota_robertson"]

        probs = np.abs(estado.amplitudes) ** 2
        barra_max = 20
        barras = "\n".join(
            f"  {s:<14} {'█' * int(p*barra_max):<20} {p*100:5.1f}%"
            for s, p in zip(estado.significantes, probs)
        )

        txt = (
            f"Signo analizado:\n{barras}\n\n"
            f"{'─'*40}\n"
            f"ΔS (incertidumbre sintagmática):  {dS:.6f}\n"
            f"ΔP (incertidumbre paradigmática): {dP:.6f}\n"
            f"ΔS · ΔP:                          {prod:.6f}\n"
            f"Cota de Robertson ½|⟨[S,P]⟩|:     {cota:.6f}\n"
            f"Factor sobre cota:                {res['factor_sobre_cota']:.2f}x\n\n"
            f"{'─'*40}\n"
            f"{res['interpretacion']}\n"
            f"{res['dominancia']}\n"
        )
        escribir_salida(self.salida, txt)
        self.m_ds.set(f"{dS:.3f}")
        self.m_dp.set(f"{dP:.3f}")
        self.m_ok.set("✓" if res["satisface_robertson"] else "✗")

    def _paradoja(self):
        if not PAQUETE_OK:
            return
        try:
            estado = self._parse_estado()
        except Exception as e:
            escribir_salida(self.salida, f"Error de entrada: {e}\n")
            return

        from saussure_quantum.uncertainty import paradoja_del_observador_linguistico
        res = paradoja_del_observador_linguistico(estado)
        orig  = res["estado_original"]
        post_s = res["despues_medir_sintagma"]
        post_p = res["despues_medir_paradigma"]

        txt = (
            "╔══════════════════════════════════════╗\n"
            "║   PARADOJA DEL OBSERVADOR             ║\n"
            "╚══════════════════════════════════════╝\n\n"
            f"Estado original:\n"
            f"  ΔS = {orig['delta_S']:.4f}   ΔP = {orig['delta_P']:.4f}\n"
            f"  ΔS·ΔP = {orig['producto']:.4f}\n\n"
            f"Tras medir SINTAGMA:\n"
            f"  ΔS = {post_s['delta_S']:.4f}   ΔP = {post_s['delta_P']:.4f}\n"
            f"  ΔS·ΔP = {post_s['producto']:.4f}\n"
            f"  Perturbación significativa: {'SÍ' if post_s['cambio_significativo'] else 'NO'}\n\n"
            f"Tras medir PARADIGMA:\n"
            f"  ΔS = {post_p['delta_S']:.4f}   ΔP = {post_p['delta_P']:.4f}\n"
            f"  ΔS·ΔP = {post_p['producto']:.4f}\n"
            f"  Perturbación significativa: {'SÍ' if post_p['cambio_significativo'] else 'NO'}\n\n"
            f"Perturbación observada en este estado: {'SÍ' if res['perturbacion_observada'] else 'NO'}\n"
            "(depende del estado: un autoestado no se altera).\n"
        )
        escribir_salida(self.salida, txt)


# ═══════════════════════════════════════════════════════════════════════════════
#  PANEL 4 — OPERADOR DIFERENCIA
# ═══════════════════════════════════════════════════════════════════════════════

class PanelDiferencia(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self._build()

    def _build(self):
        cab = tk.Frame(self, bg=COLORES["bg"])
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(24,0))
        tit = label_titulo(cab, "⊗  Operador diferencia D̂", COLORES["acento4"])
        tit.pack(anchor="w")
        agregar_tooltip(tit, "op_panel")
        desc = label_sec(cab, "Materializa el principio saussureano: ser por no ser  (?)")
        desc.pack(anchor="w", pady=(2,0))
        agregar_tooltip(desc, "op_panel")

        ctrl = seccion(self, "SISTEMA DE SIGNOS", COLORES["acento4"])
        ctrl.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        fila_sigs = tk.Frame(ctrl, bg=COLORES["panel"])
        lbl_op = tk.Label(fila_sigs, text="Signos (uno x línea)  (?)", font=FUENTE_LABEL,
                 bg=COLORES["panel"], fg=COLORES["texto_sec"],
                 width=22, anchor="w")
        lbl_op.pack(side="left", padx=(10,0))
        agregar_tooltip(lbl_op, "op_signos")
        self.entry_sigs = tk.Text(fila_sigs, font=FUENTE_LABEL,
                                   bg=COLORES["entrada"], fg=COLORES["texto"],
                                   insertbackground=COLORES["acento4"],
                                   relief="flat", width=30, height=4)
        self.entry_sigs.insert("1.0", "/p/\n/b/\n/t/")
        self.entry_sigs.pack(side="left", padx=8, pady=6)
        agregar_tooltip(self.entry_sigs, "op_signos")
        fila_sigs.pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=COLORES["bg"])
        btn_row.grid(row=2, column=0, sticky="nw", padx=24, pady=(0,8))
        boton(btn_row, "  Aplicar D̂  ", self._aplicar,
              COLORES["acento4"]).pack(side="left", padx=(0,8))
        btn_neg = boton(btn_row, "  Análisis de negatividad  ", self._negatividad,
              COLORES["borde"])
        btn_neg.pack(side="left", padx=(0,8))
        agregar_tooltip(btn_neg, "op_negatividad")
        btn_sim = boton(btn_row, "  Similitud diferencial  ", self._similitud,
              COLORES["borde"])
        btn_sim.pack(side="left", padx=(0,8))
        agregar_tooltip(btn_sim, "op_similitud")
        boton(btn_row, "  Ver matriz D̂  ", self._ver_matriz,
              COLORES["borde"]).pack(side="left")

        sal = seccion(self, "RESULTADO", COLORES["acento4"])
        sal.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0,8))
        self.rowconfigure(3, weight=1)
        self.salida = area_salida(sal, height=12)
        self.salida.pack(fill="both", expand=True, padx=10, pady=10)

        met_frame = tk.Frame(self, bg=COLORES["bg"])
        met_frame.grid(row=4, column=0, sticky="ew", padx=24, pady=(0,20))
        for i in range(3):
            met_frame.columnconfigure(i, weight=1)
        self.m_dim  = tk.StringVar(value="—")
        self.m_neg  = tk.StringVar(value="—")
        self.m_dom  = tk.StringVar(value="—")
        metric_card(met_frame, "Dimensión", self.m_dim, COLORES["acento4"]).grid(
            row=0, column=0, sticky="ew", padx=(0,6))
        metric_card(met_frame, "Negatividad total", self.m_neg, COLORES["acento4"]).grid(
            row=0, column=1, sticky="ew", padx=3)
        metric_card(met_frame, "Signo dominante", self.m_dom, COLORES["acento"]).grid(
            row=0, column=2, sticky="ew", padx=(6,0))

    def _get_signos(self):
        txt = self.entry_sigs.get("1.0", "end").strip()
        sigs = [s.strip() for s in txt.splitlines() if s.strip()]
        if len(sigs) < 2:
            raise ValueError("Ingresá al menos 2 signos")
        estados = []
        for i, s in enumerate(sigs):
            amps = [0.0] * len(sigs)
            amps[i] = 1.0
            estados.append(SignoCuanto(sigs, amps))
        return sigs, estados

    def _aplicar(self):
        if not PAQUETE_OK:
            return
        try:
            sigs, estados = self._get_signos()
        except Exception as e:
            escribir_salida(self.salida, f"Error: {e}\n")
            return

        resultado = operador_diferencia(estados)
        probs = np.abs(resultado.amplitudes) ** 2
        barra_max = 20

        lineas = [
            "D̂ aplicado al sistema de signos\n",
            f"{'─'*42}\n",
            "Estado resultante (pura diferencia):\n",
        ]
        for s, p, a in zip(sigs, probs, resultado.amplitudes):
            barra = "█" * int(p * barra_max)
            lineas.append(f"  {s:<12} {barra:<20} {p*100:5.1f}%  amp={a.real:+.3f}")

        lineas.append(f"\n{'─'*42}")
        lineas.append(f"Norma: {np.linalg.norm(resultado.amplitudes):.6f}")
        lineas.append("\nCada signo ES por NO SER los demás.")
        lineas.append("La 'sustancia' se disuelve en relaciones puras.")

        escribir_salida(self.salida, "\n".join(lineas))
        self.m_dim.set(str(len(sigs)))
        neg = principio_negatividad(resultado)
        self.m_neg.set(f"{neg['negatividad_total']:.2f}")
        self.m_dom.set(neg["significante_principal"])

    def _negatividad(self):
        if not PAQUETE_OK:
            return
        try:
            sigs, estados = self._get_signos()
        except Exception as e:
            escribir_salida(self.salida, f"Error: {e}\n")
            return

        resultado = operador_diferencia(estados)
        neg = principio_negatividad(resultado)
        barra_max = 20

        lineas = [
            "ANÁLISIS DE NEGATIVIDAD\n",
            "Cuánto 'debe' cada signo a no ser los otros:\n",
            f"{'─'*42}\n",
        ]
        for s, n in neg["negatividad_por_significante"].items():
            barra = "█" * int(n / max(neg["negatividad_por_significante"].values()) * barra_max)
            lineas.append(f"  {s:<12} {barra:<22} {n:.4f}")

        lineas.append(f"\n{'─'*42}")
        lineas.append(f"Negatividad total:   {neg['negatividad_total']:.4f}")
        lineas.append(f"Signo principal:     {neg['significante_principal']}")
        escribir_salida(self.salida, "\n".join(lineas))
        self.m_neg.set(f"{neg['negatividad_total']:.2f}")
        self.m_dom.set(neg["significante_principal"])

    def _similitud(self):
        if not PAQUETE_OK:
            return
        try:
            sigs, estados = self._get_signos()
        except Exception as e:
            escribir_salida(self.salida, f"Error: {e}\n")
            return

        from saussure_quantum.operators import similitud_diferencial
        lineas = ["SIMILITUD DIFERENCIAL\n",
                  "Qué tan similares son los signos entre sí:\n",
                  f"{'─'*42}\n"]
        for i in range(len(estados)):
            for j in range(i+1, len(estados)):
                sim = similitud_diferencial(estados[i], estados[j])
                barra = "█" * int(sim * 20)
                lineas.append(f"  {sigs[i]:<8} ↔ {sigs[j]:<8}  {barra:<22} {sim:.4f}")

        lineas.append(f"\n{'─'*42}")
        lineas.append("1.0 = idénticos en diferencia")
        lineas.append("0.0 = ortogonales, sin relación")
        escribir_salida(self.salida, "\n".join(lineas))

    def _ver_matriz(self):
        """Mostrar la matriz completa del operador D̂ para el sistema actual."""
        if not PAQUETE_OK:
            return
        try:
            sigs, estados = self._get_signos()
        except Exception as e:
            escribir_salida(self.salida, f"Error: {e}\n")
            return

        lang = Langue(len(sigs), terminos=sigs)
        op   = OperadorDiferencia(lang)
        D    = op.matriz()
        d    = len(sigs)

        # Encabezado
        lineas = [
            "MATRIZ DEL OPERADOR D̂\n",
            f"D = d·I - J   (d={d}, I=identidad, J=matriz de unos)\n",
            f"{'─'*42}\n",
        ]

        # Fila de encabezado de columnas
        col_w = 8
        header = " " * 14 + "".join(f"{s[:6]:>{col_w}}" for s in sigs)
        lineas.append(header)
        lineas.append("  " + "─" * (12 + col_w * d))

        # Filas de la matriz
        for i, sig_fila in enumerate(sigs):
            fila = f"  {sig_fila[:12]:<12}│"
            for j in range(d):
                val = D[i, j].real
                fila += f"{val:>{col_w}.1f}"
            lineas.append(fila)

        # Propiedades
        autovalores = sorted(set(np.linalg.eigvals(D).real.round(4)))
        traza = np.trace(D).real
        lineas += [
            f"\n{'─'*42}",
            f"Traza:        {traza:.1f}",
            f"Autovalores:  {[round(v,2) for v in autovalores]}",
            f"\nInterpretación:",
            f"  Diagonal = {d-1:.0f}  (cada signo se opone a {d-1} otros)",
            f"  Fuera de diagonal = -1  (fuerza de oposición entre pares)",
        ]

        escribir_salida(self.salida, "\n".join(lineas))
        self.m_dim.set(str(d))


# ═══════════════════════════════════════════════════════════════════════════════
#  PANEL 5 — TEORÍA
# ═══════════════════════════════════════════════════════════════════════════════

TEORIA_CONTENIDO = {
    "¿Qué es esto?": """\
Saussure–Quantum Fusion es una implementación computacional
de la fusión entre la semiótica estructural de Ferdinand de
Saussure (1857–1913) y la mecánica cuántica (Bohr, Heisenberg).

TESIS CENTRAL:
  "La realidad no es una sustancia, sino un efecto de segundo
   orden que emerge de la diferencia observada."

El mundo no está hecho de objetos con propiedades intrínsecas,
sino de relaciones de oposición que colapsan en el acto de
ser observadas o enunciadas.

Ambos sistemas — el lingüístico y el cuántico — comparten
una estructura matemática profundamente isomórfica.""",

    "Saussure": """\
Ferdinand de Saussure (1857–1913) propuso que el lenguaje
es un sistema de diferencias puras, sin términos positivos.

CONCEPTOS CLAVE:

Signo lingüístico:
  Unidad de dos caras: significante (imagen acústica)
  y significado (concepto). Su valor es puramente
  relacional — no existe por sí mismo.

Langue vs Parole:
  Langue = el sistema (potencial, social, virtual)
  Parole = el acto de habla (actual, individual, real)

Ejes paradigmático y sintagmático:
  Paradigma: relaciones de sustitución (¿qué puede
             reemplazar a esta palabra?)
  Sintagma:  relaciones de posición (¿dónde está
             en la cadena hablada?)

Principio de negatividad:
  "En la lengua solo hay diferencias sin términos
   positivos." — Saussure, Cours de Linguistique, 1916""",

    "Mecánica cuántica": """\
La mecánica cuántica describe la física a escala subatómica.
Sus principios más relevantes para esta fusión son:

Estado cuántico (|ψ⟩):
  Un sistema existe en superposición de todos sus estados
  posibles hasta ser medido. La medición colapsa la
  superposición a un resultado concreto.

Relación de incertidumbre (Robertson):
  ΔS · ΔP ≥ ½|⟨[S,P]⟩|
  En mecánica cuántica continua [x,p]=iℏ da la cota ℏ/2.
  En este modelo de dimensión finita esa relación canónica
  es imposible y la cota depende del estado (puede ser 0).

Colapso por observación:
  "No hay fenómeno cuántico sin observación." — Bohr
  El observador es constitutivo de la realidad medida.

Amplitudes de probabilidad:
  Los estados se describen con números complejos αᵢ ∈ ℂ.
  La probabilidad de medir el estado i es |αᵢ|².""",

    "La fusión": """\
TABLA DE ANALOGÍAS:

  Saussure              Cuántico           Implementación
  ─────────────────────────────────────────────────────
  Signo lingüístico  ↔  Estado cuántico   SignoCuanto
  Langue             ↔  Espacio Hilbert   Langue
  Parole             ↔  Colapso/medición  colapso_parole()
  Negatividad (D̂)    ↔  Amplitud prob.   operador_diferencia()
  Eje sintagmático   ↔  Posición (Ŝ)     ObservablesSaussureanos.S
  Eje paradigmático  ↔  Momento (P̂)     ObservablesSaussureanos.P
  Indeterminación    ↔  Incertidumbre    incertidumbre_s_h()

FORMALISMO MATEMÁTICO:

  |signo⟩ = Σᵢ αᵢ |sᵢ⟩        (superposición)
  D̂ = d·I - J                  (operador diferencia)
  ΔS · ΔP ≥ ℏ_semiótico / 2   (principio incertidumbre)

NOTA MATEMÁTICA:
  La relación [Ŝ, P̂] = iℏI es imposible en dim. finita
  (Tr([S,P])=0 pero Tr(iℏI)=iℏd≠0). El operador P usa
  condiciones periódicas que minimizan el error de borde.""",

    "Herramientas": """\
◈ POETA CUÁNTICO
  Genera versos usando colapsos probabilísticos.
  Cada palabra comienza en superposición y colapsa
  al ser "dicha". La temperatura ℏ controla el caos.
  Podés personalizar el diccionario por categoría.

◉ SIMULADOR DE INCERTIDUMBRE
  Calcula ΔS, ΔP y la cota de Robertson para distintos
  tipos de estado. Compará los 4 tipos en una sola tabla
  y observá que la cota depende del estado.

△ PRINCIPIO DE INCERTIDUMBRE
  Analizá tu propio conjunto de signos. Ingresá los
  significantes y sus amplitudes, o cargá uno de los
  7 ejemplos predefinidos. La paradoja del observador
  muestra cómo medir un eje perturba el otro.

⊗ OPERADOR DIFERENCIA
  Ingresá un sistema de signos y aplicá D̂ para ver
  cómo cada signo se disuelve en pura diferencia.
  Visualizá la matriz completa, la negatividad de
  cada signo y la similitud diferencial entre pares.""",
}


class PanelTeoria(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORES["bg"])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        cab = tk.Frame(self, bg=COLORES["bg"])
        cab.grid(row=0, column=0, sticky="ew", padx=24, pady=(24,0))
        label_titulo(cab, "❖  Teoría y conceptos", COLORES["texto"]).pack(anchor="w")
        label_sec(cab, "Fundamentos de la fusión Saussure–Cuántica").pack(
            anchor="w", pady=(2,12))

        # Navegación por subtemas
        nav = tk.Frame(cab, bg=COLORES["bg"])
        nav.pack(fill="x")
        self.var_tema = tk.StringVar(value=list(TEORIA_CONTENIDO.keys())[0])
        self.nav_btns = {}
        for tema in TEORIA_CONTENIDO:
            btn = tk.Label(
                nav, text=tema, font=FUENTE_SMALL,
                bg=COLORES["panel"], fg=COLORES["texto_sec"],
                padx=10, pady=6, cursor="hand2",
                relief="flat",
                highlightbackground=COLORES["borde"],
                highlightthickness=1
            )
            btn.pack(side="left", padx=(0,4))
            btn.bind("<Button-1>", lambda e, t=tema: self._mostrar_tema(t))
            btn.bind("<Enter>",    lambda e, b=btn: b.configure(fg=COLORES["texto"]))
            btn.bind("<Leave>",    lambda e, b=btn, t=tema: self._hover_leave_btn(b, t))
            self.nav_btns[tema] = btn

        # Zona de contenido
        sal = seccion(self, "CONTENIDO", COLORES["texto"])
        sal.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
        self.salida = area_salida(sal, height=20)
        self.salida.pack(fill="both", expand=True, padx=10, pady=10)

        # Mostrar primer tema
        self._mostrar_tema(list(TEORIA_CONTENIDO.keys())[0])

    def _mostrar_tema(self, tema):
        self.var_tema.set(tema)
        # Actualizar estilos de botones
        for t, btn in self.nav_btns.items():
            if t == tema:
                btn.configure(bg=COLORES["acento"], fg=COLORES["bg"])
            else:
                btn.configure(bg=COLORES["panel"], fg=COLORES["texto_sec"])
        escribir_salida(self.salida, TEORIA_CONTENIDO[tema])

    def _hover_leave_btn(self, btn, tema):
        if tema != self.var_tema.get():
            btn.configure(fg=COLORES["texto_sec"])

if __name__ == "__main__":
    app = AppSaussureQuantum()
    app.mainloop()
