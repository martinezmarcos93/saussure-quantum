"""
uncertainty.py - Incertidumbre semiótica en un modelo quantum-like

Implementa:
- El análogo lingüístico del principio de incertidumbre cuántico
- Observables complementarios: Paradigma (momento) vs Sintagma (posición)
- Cota de Robertson calculada desde el conmutador efectivo
- Una relación de compromiso entre ambas dimensiones del signo que depende
  del estado: en dimensión finita NO existe una cota universal ΔS·ΔP ≥ ℏ/2
  (un estado base tiene ΔS = 0 y ΔP = ℏ/√2, producto 0)
"""

import warnings

import numpy as np
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass
from saussure_quantum.core import SignoCuanto, Langue


# Constante de Planck semiótica (unidad mínima de sentido)
HBAR_SEMIOTICO = 1.0  # Puede ajustarse para calibrar la incertidumbre


class ObservablesSaussureanos:
    """
    Observables complementarios del sistema lingüístico.
    
    Ŝ (Sintagma) = análogo a la posición
    P̂ (Paradigma) = análogo al momento
    
    No satisfacen exactamente una relación canónica en dimensión finita. La cota
    utilizada es la desigualdad de Robertson basada en el conmutador efectivo.
    """
    
    def __init__(self, dimension: int, hbar: float = HBAR_SEMIOTICO):
        """
        Inicializar los observables.
        
        Args:
            dimension: Dimensión del espacio de Hilbert lingüístico
            hbar: Constante de Planck semiótica
        """
        if isinstance(dimension, (bool, np.bool_)) or not isinstance(dimension, (int, np.integer)) or dimension < 1:
            raise ValueError(f"dimension debe ser un entero >= 1; se recibió {dimension!r}.")
        if not np.isfinite(hbar) or hbar <= 0:
            raise ValueError("hbar debe ser un número finito > 0.")
        self.dimension = int(dimension)
        self.hbar = hbar
        if self.dimension < 3:
            warnings.warn(
                "Con dimension < 3 la diferencia centrada periódica es idénticamente "
                "nula (los vecinos i+1 e i-1 coinciden): P = 0 y el análisis de "
                "incertidumbre es trivial.",
                RuntimeWarning,
                stacklevel=2,
            )

        # Construir operadores
        self.S = self._construir_sintagma()
        self.P = self._construir_paradigma()
        
        # En dimensión finita no puede existir [S,P] = iℏI exactamente.
        # Guardamos el conmutador efectivo para aplicar Robertson estado por estado.
        self._conmutador = self._calcular_conmutador()
    
    def _construir_sintagma(self) -> np.ndarray:
        """
        Operador Sintagma (posición lingüística).
        
        Representa la posición del signo en la cadena hablada,
        su relación con los elementos adyacentes.
        
        En base discreta: matriz diagonal con valores 0,...,d-1
        """
        # Posiciones sintagmáticas (orden en la frase)
        return np.diag(np.arange(self.dimension))
    
    def _construir_paradigma(self) -> np.ndarray:
        """
        Operador Paradigma (momento lingüístico).

        Representa la capacidad de sustitución del signo,
        sus alternativas posibles en el sistema.

        Análogo al operador momento: P = -iℏ·d/dx
        En base discreta: diferencias finitas con condiciones de borde periódicas.

        Nota matemática — limitación fundamental:
            La relación [S, P] = iℏ·I es IMPOSIBLE en dimensión finita.
            Prueba: Tr([S,P]) = Tr(SP) - Tr(PS) = 0 (ciclicidad de la traza),
            pero Tr(iℏI) = iℏ·d ≠ 0 para cualquier d finita.
            Ninguna implementación discreta puede satisfacerla exactamente.
            Se usan condiciones periódicas porque son consistentes con la
            física de un sistema discreto circular (lattice) y minimizan
            los artefactos de borde frente al operador tridiagonal abierto.

        Espectro: las ondas planas e^{2πikj/d}/√d son autovectores con
        autovalor ℏ·sin(2πk/d).

        Dimensiones 1 y 2: los vecinos i+1 e i−1 coinciden módulo d, así que
        las dos contribuciones se cancelan y P = 0. Las entradas se ACUMULAN
        (+=) precisamente por eso: asignarlas (=) hacía que la segunda pisara
        a la primera y dejaba una matriz anti-Hermitiana (P = iℏ/2·X en d=2),
        cuyos "valores esperados" eran imaginarios y se truncaban en silencio.
        """
        P = np.zeros((self.dimension, self.dimension), dtype=complex)
        d = self.dimension
        for i in range(d):
            # Diferencias finitas centradas con borde periódico:
            # evita los efectos de borde del operador tridiagonal abierto
            P[i, (i + 1) % d] += -1j * self.hbar / 2
            P[i, (i - 1) % d] +=  1j * self.hbar / 2
        return P

    def _calcular_conmutador(self) -> np.ndarray:
        """Calcular [S, P] = S·P - P·S"""
        return self.S @ self.P - self.P @ self.S

    def verificar_conmutacion(self, tolerancia: float = 1e-10) -> bool:
        """
        Verificar que [S, P] ≈ i·ℏ·I e informar el error cuantitativo.

        Nota: en dimensión finita [S,P] = iℏI es matemáticamente imposible
        (ver docstring de _construir_paradigma). Este método siempre retornará
        False para cualquier implementación discreta. Se mantiene por
        compatibilidad de API; usar error_conmutacion() para diagnóstico.

        Returns:
            True si el error es menor que tolerancia (nunca en dimensión finita)
        """
        esperado = 1j * self.hbar * np.eye(self.dimension)
        diferencia = np.linalg.norm(self._conmutador - esperado)
        return diferencia < tolerancia

    def error_conmutacion(self) -> float:
        """
        Retorna la norma de Frobenius de ([S,P] - iℏI).

        Más útil que verificar_conmutacion() para sistemas discretos, donde
        el error es no nulo por construcción pero acotado y reproducible.
        Un valor menor indica mejor aproximación a la relación canónica.

        Returns:
            Error cuantitativo de la relación de conmutación
        """
        esperado = 1j * self.hbar * np.eye(self.dimension)
        return float(np.linalg.norm(self._conmutador - esperado))
    
    def incertidumbre(self, estado: SignoCuanto) -> Tuple[float, float, float]:
        """
        Calcular ΔS · ΔP para un estado dado.
        
        Args:
            estado: Estado cuántico-semiótico
        
        Returns:
            (ΔS, ΔP, ΔS·ΔP)

        La cota relevante para estos operadores finitos no es ℏ/2 en general.
        Se calcula a partir del conmutador real mediante Robertson:
            ΔS·ΔP ≥ 1/2 |⟨[S,P]⟩|.
        """
        if estado.dimension != self.dimension:
            raise ValueError("Dimensión del estado incompatible con los observables.")
        psi = estado.amplitudes

        # Valor esperado de S
        exp_S = np.vdot(psi, self.S @ psi).real
        exp_S2 = np.vdot(psi, self.S @ self.S @ psi).real
        var_S = exp_S2 - exp_S**2
        delta_S = np.sqrt(max(var_S, 0))
        
        # Valor esperado de P
        exp_P = np.vdot(psi, self.P @ psi).real
        exp_P2 = np.vdot(psi, self.P @ self.P @ psi).real
        var_P = exp_P2 - exp_P**2
        delta_P = np.sqrt(max(var_P, 0))
        
        producto = delta_S * delta_P

        return float(delta_S), float(delta_P), float(producto)
    
    def estado_minima_incertidumbre(self) -> SignoCuanto:
        """
        Genera un estado gaussiano discreto como candidato de compromiso.

        No se afirma que este estado sature la cota de Robertson. La saturación
        es una propiedad que debe demostrarse para un par de observables y un
        estado concretos; esta construcción sólo proporciona un estado de
        referencia suave y localizado.
        """
        # Estado gaussiano en representación de posición (sintagma)
        x = np.linspace(-3, 3, self.dimension)
        psi = np.exp(-x**2 / 2)  # Gaussian packet
        psi = psi / np.linalg.norm(psi)
        
        # Usar significantes genéricos
        significantes = [f"pos_{i}" for i in range(self.dimension)]
        
        return SignoCuanto(significantes, psi.tolist())


class PrincipioIncertidumbreSaussure:
    """
    Implementa el principio fundamental de la fusión:
    No se puede conocer simultáneamente el valor paradigmático
    y sintagmático de un signo con precisión arbitraria.
    """
    
    def __init__(self, langue: Langue, hbar: float = HBAR_SEMIOTICO):
        """
        Args:
            langue: Sistema lengua sobre el que opera
            hbar: Constante de Planck semiótica
        """
        self.langue = langue
        self.hbar = hbar
        self.obs = ObservablesSaussureanos(langue.dimension, hbar)
    
    def analizar_estado(self, estado: SignoCuanto) -> Dict:
        """
        Análisis completo de incertidumbre para un estado.
        
        Returns:
            Diccionario con valores de incertidumbre y análisis cualitativo
        """
        delta_S, delta_P, producto = self.obs.incertidumbre(estado)
        psi = estado.amplitudes
        comm_expectation = np.vdot(psi, self.obs._conmutador @ psi)
        cota_robertson = 0.5 * abs(comm_expectation)
        
        # Interpretación cualitativa
        if cota_robertson > 1e-12 and producto <= cota_robertson * 1.1:
            interpretacion = "CERCANO A LA COTA DE ROBERTSON"
        elif producto > max(cota_robertson, 1e-12) * 10:
            interpretacion = "ALTA INCERTIDUMBRE RELATIVA A LA COTA"
        else:
            interpretacion = "INCERTIDUMBRE MODERADA"
        
        # Análisis de dominancia
        if delta_S < delta_P:
            dominancia = "predomina precisión sintagmática (posición bien definida)"
        else:
            dominancia = "predomina precisión paradigmática (momento bien definido)"
        
        return {
            "delta_sintagma": delta_S,
            "delta_paradigma": delta_P,
            "producto_incertidumbre": producto,
            "cota_robertson": float(cota_robertson),
            "valor_conmutador": complex(comm_expectation),
            "satisface_robertson": bool(producto + 1e-10 >= cota_robertson),
            "factor_sobre_cota": float(producto / cota_robertson) if cota_robertson > 1e-12 else float('inf'),
            "interpretacion": interpretacion,
            "dominancia": dominancia
        }
    
    def estado_maxima_incertidumbre(self) -> SignoCuanto:
        """
        Superposición uniforme sobre los términos de la langue.

        Nombre histórico: NO maximiza el producto de incertidumbres. La
        superposición uniforme es la onda plana de momento k = 0, autovector
        de P con autovalor 0, de modo que ΔP = 0 y ΔS·ΔP = 0. Es un estado de
        paradigma perfectamente definido y sintagma disperso
        (ΔS = √((d²−1)/12)).
        """
        amplitudes = np.ones(self.langue.dimension, dtype=complex) / np.sqrt(self.langue.dimension)
        return SignoCuanto(self.langue._base, amplitudes)
    
    def estado_sintagmatico_puro(self, posicion: int) -> SignoCuanto:
        """
        Estado con sintagma (posición) perfectamente definido.

        ΔS = 0 y ΔP = ℏ/√2 (para d ≥ 3). Esa dispersión paradigmática es
        finita y no es la máxima posible (max ΔP = ℏ si d es múltiplo de 4), así que el producto
        ΔS·ΔP vale 0: no hay cota inferior universal en dimensión finita.
        """
        if isinstance(posicion, (bool, np.bool_)) or not isinstance(posicion, (int, np.integer)) or not 0 <= posicion < self.langue.dimension:
            raise ValueError(f"Posición {posicion} fuera de rango")
        
        amplitudes = np.zeros(self.langue.dimension, dtype=complex)
        amplitudes[posicion] = 1.0
        return SignoCuanto(self.langue._base, amplitudes)
    
    def estado_paradigmatico_puro(self, momento: int) -> SignoCuanto:
        """
        Estado con paradigma (momento) perfectamente definido.

        Onda plana discreta: autovector de P con autovalor ℏ·sin(2πk/d), por
        lo que ΔP = 0. La distribución sintagmática es uniforme,
        ΔS = √((d²−1)/12), que no es la dispersión máxima posible ((d−1)/2).
        """
        # Estados de momento son ondas planas discretas
        k = 2 * np.pi * momento / self.langue.dimension
        amplitudes = np.exp(1j * k * np.arange(self.langue.dimension))
        amplitudes = amplitudes / np.linalg.norm(amplitudes)
        return SignoCuanto(self.langue._base, amplitudes)
    
    def demostrar_principio(self) -> Dict:
        """
        Tres estados de referencia con su incertidumbre y su cota de Robertson.

        Ilustra el compromiso entre sintagma y paradigma, no una cota
        universal: en los dos estados puros el producto ΔS·ΔP es 0, y el
        estado gaussiano de referencia tiene un producto MAYOR que ambos.
        """
        resultados = {}
        
        # Caso 1: Sintagma bien definido
        estado_sintagma = self.estado_sintagmatico_puro(0)
        analisis_sintagma = self.analizar_estado(estado_sintagma)
        resultados["sintagma_puro"] = {
            "descripcion": "Signo con posición sintagmática perfectamente definida",
            "delta_sintagma": analisis_sintagma["delta_sintagma"],
            "delta_paradigma": analisis_sintagma["delta_paradigma"],
            "producto": analisis_sintagma["producto_incertidumbre"],
            "cota_robertson": analisis_sintagma["cota_robertson"],
        }
        
        # Caso 2: Paradigma bien definido
        estado_paradigma = self.estado_paradigmatico_puro(0)
        analisis_paradigma = self.analizar_estado(estado_paradigma)
        resultados["paradigma_puro"] = {
            "descripcion": "Signo con valor paradigmático perfectamente definido",
            "delta_sintagma": analisis_paradigma["delta_sintagma"],
            "delta_paradigma": analisis_paradigma["delta_paradigma"],
            "producto": analisis_paradigma["producto_incertidumbre"],
            "cota_robertson": analisis_paradigma["cota_robertson"],
        }
        
        # Caso 3: Estado de compromiso (mínima incertidumbre)
        estado_minimo = self.obs.estado_minima_incertidumbre()
        analisis_minimo = self.analizar_estado(estado_minimo)
        resultados["minima_incertidumbre"] = {
            "descripcion": "Estado gaussiano de referencia (clave histórica: no minimiza ΔS·ΔP)",
            "delta_sintagma": analisis_minimo["delta_sintagma"],
            "delta_paradigma": analisis_minimo["delta_paradigma"],
            "producto": analisis_minimo["producto_incertidumbre"],
            "cota_robertson": analisis_minimo["cota_robertson"],
        }
        
        return resultados
    
    def visualizar_espacio_fase(self, estado: SignoCuanto) -> np.ndarray:
        """
        Función de Wigner discreta (distribución de cuasi-probabilidad).

            W(x, p) = (1/d) Σ_ξ ψ(x+ξ) ψ*(x−ξ) e^{−2πi·c·pξ/d}   (índices mod d)

        con c = 2 si d es impar y c = 1 si d es par.

        Propiedades (verificadas en los tests):
        - es real y suma 1;
        - la marginal en x es |ψ_x|² para toda dimensión;
        - la marginal en p es |ψ̃_p|² (transformada de Fourier discreta) sólo
          para d IMPAR. Para d par no existe una función de Wigner d×d con
          ambas marginales correctas (2ξ no recorre Z_d); se usa c = 1 para
          conservar al menos la marginal en x, y el resultado debe leerse
          sólo como visualización.

        Una versión anterior normalizaba con 2/d (la suma total daba 2) y
        usaba c = 1 siempre, que no reproduce la marginal en p ni para d impar.

        Returns:
            Matriz de distribución en espacio sintagma-paradigma
        """
        psi = estado.amplitudes
        d = self.langue.dimension
        W = np.zeros((d, d), dtype=float)
        c = 2 if d % 2 == 1 else 1
        
        for x in range(d):
            for p in range(d):
                # Transformada de Wigner para sistemas discretos.
                # Se usa aritmética modular (% d) en ambos índices para:
                #   - evitar IndexError en psi[x + xi] cuando x+xi >= d
                #   - evitar el wrap silencioso de Python en psi[x - xi] cuando x-xi < 0,
                #     que accedería a posiciones incorrectas del array sin lanzar excepción.
                suma = 0
                for xi in range(d):
                    fase = np.exp(-2j * np.pi * c * p * xi / d)
                    suma += psi[(x + xi) % d] * np.conj(psi[(x - xi) % d]) * fase
                W[x, p] = (1 / d) * suma.real
        
        return W


# Funciones de alto nivel para fácil uso
def incertidumbre_saussure_heisenberg(
    estado: SignoCuanto,
    hbar: float = HBAR_SEMIOTICO
) -> Dict:
    """
    Función principal para calcular la incertidumbre de un signo.
    
    Args:
        estado: Signo-cuanto a analizar
        hbar: Constante de Planck semiótica
    
    Returns:
        Diccionario con resultados del principio de incertidumbre
    
    Example:
        >>> signo = SignoCuanto(["a","b","c"], [1,1,1])
        >>> incertidumbre_saussure_heisenberg(signo)
    """
    # Crear lengua temporal
    lang = Langue(estado.dimension)
    principio = PrincipioIncertidumbreSaussure(lang, hbar)
    return principio.analizar_estado(estado)


def paradoja_del_observador_linguistico(estado: SignoCuanto) -> Dict:
    """
    Compara las incertidumbres antes y después de proyectar sobre S y sobre P.

    Se proyecta sobre el autovector MÁS PROBABLE de cada observable (no se
    muestrea), así que el resultado es determinista. Que la medición altere
    la dispersión del observable complementario depende del estado: no ocurre
    siempre (p. ej. un autoestado de P no cambia al "medir" P).

    Args:
        estado: Estado inicial

    Returns:
        Comparación de incertidumbres antes/después de mediciones. La clave
        `perturbacion_observada` se CALCULA a partir de este estado; la versión
        anterior devolvía `principio_demostrado: True` de forma incondicional.
    """
    lang = Langue(estado.dimension)
    principio = PrincipioIncertidumbreSaussure(lang)
    
    # Estado original
    original = principio.analizar_estado(estado)
    
    # Simular medición de sintagma
    S = principio.obs.S
    psi = estado.amplitudes
    
    # Proyectar sobre autovalor de S (medir posición)
    autovalores_S, autovectores_S = np.linalg.eigh(S)
    probs_S = np.abs(autovectores_S.conj().T @ psi) ** 2
    idx_S = np.argmax(probs_S)  # Resultado más probable
    estado_S = SignoCuanto(estado.significantes.copy(), autovectores_S[:, idx_S])
    despues_S = principio.analizar_estado(estado_S)
    
    # Proyectar sobre autovalor de P (medir momento)
    P = principio.obs.P
    autovalores_P, autovectores_P = np.linalg.eigh(P)
    probs_P = np.abs(autovectores_P.conj().T @ psi) ** 2
    idx_P = np.argmax(probs_P)
    estado_P = SignoCuanto(estado.significantes.copy(), autovectores_P[:, idx_P])
    despues_P = principio.analizar_estado(estado_P)
    
    return {
        "estado_original": {
            "delta_S": original["delta_sintagma"],
            "delta_P": original["delta_paradigma"],
            "producto": original["producto_incertidumbre"]
        },
        "despues_medir_sintagma": {
            "delta_S": despues_S["delta_sintagma"],
            "delta_P": despues_S["delta_paradigma"],
            "producto": despues_S["producto_incertidumbre"],
            # Usar claves de analizar_estado() (delta_paradigma/delta_sintagma),
            # no las del dict de salida (delta_P/delta_S) que aún no existen aquí.
            "cambio_significativo": bool(despues_S["delta_paradigma"] > original["delta_paradigma"] * 1.5)
        },
        "despues_medir_paradigma": {
            "delta_S": despues_P["delta_sintagma"],
            "delta_P": despues_P["delta_paradigma"],
            "producto": despues_P["producto_incertidumbre"],
            "cambio_significativo": bool(despues_P["delta_sintagma"] > original["delta_sintagma"] * 1.5)
        },
        "perturbacion_observada": bool(
            despues_S["delta_paradigma"] > original["delta_paradigma"] * 1.5
            or despues_P["delta_sintagma"] > original["delta_sintagma"] * 1.5
        ),
    }


# Alias conceptuales
incertidumbre_linguistica = incertidumbre_saussure_heisenberg
principio_saussure_heisenberg = incertidumbre_saussure_heisenberg