"""Experimento S003: respuestas conjuntas e igualdad QQ.

Diseño
------
Dos preguntas dicotómicas, A y B, respondidas en dos órdenes por grupos
independientes. Se registran las DOS respuestas de cada orden, de modo que
cada orden aporta una distribución conjunta sobre cuatro resultados:

    orden A→B:  p_AB[i, j] = P(primera respuesta = i a A, segunda = j a B)
    orden B→A:  p_BA[i, j] = P(primera respuesta = i a B, segunda = j a A)

con índice 0 = "sí" y 1 = "no". Hay 3 + 3 = 6 observables libres (S002 tenía 2).

Igualdad QQ (Wang y Busemeyer, 2013, Topics in Cognitive Science 5, 689–710)
----------------------------------------------------------------------------
    p(AyBn) + p(AnBy) = p(ByAn) + p(BnAy)

es decir, la probabilidad de dar respuestas DISTINTAS a las dos preguntas es
la misma en ambos órdenes. El residuo es q = d_AB − d_BA.

Se deriva de cuatro supuestos: (1) el estado inicial es el mismo en ambos
órdenes; (2) cada respuesta es un proyector ortogonal y los de una pregunta
suman la identidad; (3) regla de Born; (4) actualización por la regla de
Lüders, sin otra dinámica ni información entre las dos preguntas. Vale para
cualquier dimensión, cualquier rango de los proyectores y estados mixtos.

Qué NO dice la igualdad (resultados de este módulo, ver docs/RESULTADOS_S003.md)
---------------------------------------------------------------------------------
- No es exclusiva de modelos cuánticos: un modelo clásico de repetición con
  probabilidad de copia simétrica la cumple exactamente y tiene efectos de
  orden; un modelo clásico de Markov general es saturado y reproduce
  cualquier dato, cumpla o no QQ.
- Cumplir QQ no es evidencia de estructura cuántica; violarla sí refuta el
  modelo proyectivo bajo los cuatro supuestos.

El módulo es puramente matemático y sintético. No contiene datos humanos ni
interpretación psicológica.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple

import numpy as np
from scipy import stats
from scipy.linalg import expm
from scipy.optimize import minimize

Conjuntas = Tuple[np.ndarray, np.ndarray]

_TOL = 1e-9


# ───────────────────────────── Datos ─────────────────────────────

@dataclass(frozen=True)
class S003Dataset:
    """Conteos conjuntos por orden. `counts[i, j]`: primera respuesta i, segunda j."""

    counts_ab: np.ndarray
    counts_ba: np.ndarray

    def __post_init__(self):
        for nombre in ("counts_ab", "counts_ba"):
            c = np.asarray(getattr(self, nombre))
            if c.shape != (2, 2):
                raise ValueError(f"{nombre} debe tener forma (2, 2).")
            if not np.all(np.isfinite(c)) or np.any(c < 0) or np.any(c != np.round(c)):
                raise ValueError(f"{nombre} debe contener enteros no negativos.")
            object.__setattr__(self, nombre, c.astype(int))

    @property
    def n_ab(self) -> int:
        return int(self.counts_ab.sum())

    @property
    def n_ba(self) -> int:
        return int(self.counts_ba.sum())


def validar_conjuntas(p_ab: np.ndarray, p_ba: np.ndarray, tol: float = 1e-8) -> Conjuntas:
    """Comprueba que ambas matrices 2×2 sean distribuciones de probabilidad."""
    salida = []
    for nombre, p in (("p_ab", p_ab), ("p_ba", p_ba)):
        p = np.asarray(p, dtype=float)
        if p.shape != (2, 2):
            raise ValueError(f"{nombre} debe tener forma (2, 2).")
        if not np.all(np.isfinite(p)):
            raise ValueError(f"{nombre} contiene valores no finitos.")
        if np.any(p < -tol) or abs(p.sum() - 1.0) > tol:
            raise ValueError(f"{nombre} no es una distribución de probabilidad válida.")
        p = np.clip(p, 0.0, None)
        salida.append(p / p.sum())
    return salida[0], salida[1]


def generar_datos_s003(
    p_ab: np.ndarray,
    p_ba: np.ndarray,
    n_por_orden: int = 1000,
    seed: Optional[int] = 2026,
) -> S003Dataset:
    """Muestras multinomiales independientes para cada orden."""
    if isinstance(n_por_orden, bool) or not isinstance(n_por_orden, (int, np.integer)) or n_por_orden < 1:
        raise ValueError("n_por_orden debe ser un entero >= 1.")
    p_ab, p_ba = validar_conjuntas(p_ab, p_ba)
    rng = np.random.default_rng(seed)
    return S003Dataset(
        rng.multinomial(n_por_orden, p_ab.ravel()).reshape(2, 2),
        rng.multinomial(n_por_orden, p_ba.ravel()).reshape(2, 2),
    )


def dividir_train_test_s003(
    data: S003Dataset,
    proporcion_train: float = 0.8,
    seed: Optional[int] = 2026,
) -> Tuple[S003Dataset, S003Dataset]:
    """Partición aleatoria reproducible; train + test = datos originales."""
    if not 0 < proporcion_train < 1:
        raise ValueError("proporcion_train debe estar estrictamente entre 0 y 1.")
    rng = np.random.default_rng(seed)
    tr_ab = rng.binomial(data.counts_ab, proporcion_train)
    tr_ba = rng.binomial(data.counts_ba, proporcion_train)
    return S003Dataset(tr_ab, tr_ba), S003Dataset(data.counts_ab - tr_ab, data.counts_ba - tr_ba)


# ─────────────────────── Modelo proyectivo ───────────────────────

def validar_estado(rho: np.ndarray, tol: float = 1e-8) -> np.ndarray:
    """Valida una matriz densidad (hermítica, traza 1, semidefinida positiva)."""
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim == 1:
        if not np.all(np.isfinite(rho)) or np.linalg.norm(rho) <= 0:
            raise ValueError("El vector de estado debe ser finito y no nulo.")
        psi = rho / np.linalg.norm(rho)
        return np.outer(psi, psi.conj())
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or not np.all(np.isfinite(rho)):
        raise ValueError("El estado debe ser un vector o una matriz cuadrada finita.")
    if not np.allclose(rho, rho.conj().T, atol=tol):
        raise ValueError("La matriz densidad debe ser hermítica.")
    if abs(np.trace(rho).real - 1.0) > tol:
        raise ValueError("La matriz densidad debe tener traza 1.")
    if np.linalg.eigvalsh((rho + rho.conj().T) / 2).min() < -tol:
        raise ValueError("La matriz densidad debe ser semidefinida positiva.")
    return rho


def validar_proyector(P: np.ndarray, dim: int, tol: float = 1e-8) -> np.ndarray:
    """Valida un proyector ortogonal: hermítico e idempotente."""
    P = np.asarray(P, dtype=complex)
    if P.shape != (dim, dim) or not np.all(np.isfinite(P)):
        raise ValueError("El proyector debe ser una matriz cuadrada finita de la dimensión del estado.")
    if not np.allclose(P, P.conj().T, atol=tol):
        raise ValueError("El proyector debe ser hermítico.")
    if not np.allclose(P @ P, P, atol=tol):
        raise ValueError("El proyector debe ser idempotente (P² = P).")
    return P


def proyector(vectores: np.ndarray) -> np.ndarray:
    """Proyector ortogonal sobre el subespacio generado por las columnas dadas."""
    v = np.asarray(vectores, dtype=complex)
    if v.ndim == 1:
        v = v[:, None]
    if not np.all(np.isfinite(v)):
        raise ValueError("Los vectores deben ser finitos.")
    q, r = np.linalg.qr(v)
    if np.any(np.abs(np.diag(r)) < 1e-12):
        raise ValueError("Los vectores deben ser linealmente independientes y no nulos.")
    return q @ q.conj().T


def probabilidades_proyectivas(rho: np.ndarray, P_a: np.ndarray, P_b: np.ndarray) -> Conjuntas:
    """Probabilidades conjuntas de dos mediciones proyectivas sucesivas.

    p_AB[i, j] = Tr(P_B^j P_A^i ρ P_A^i P_B^j), con P^0 = P ("sí") y P^1 = I − P.
    La regla de Lüders está implícita en el producto de proyectores.
    """
    rho = validar_estado(rho)
    dim = rho.shape[0]
    P_a, P_b = validar_proyector(P_a, dim), validar_proyector(P_b, dim)
    identidad = np.eye(dim)
    pa, pb = (P_a, identidad - P_a), (P_b, identidad - P_b)

    def conjunta(primero, segundo):
        return np.array([
            [np.trace(segundo[j] @ primero[i] @ rho @ primero[i] @ segundo[j]).real for j in range(2)]
            for i in range(2)
        ])

    return validar_conjuntas(conjunta(pa, pb), conjunta(pb, pa))


def norma_conmutador(P_a: np.ndarray, P_b: np.ndarray) -> float:
    """Norma de Frobenius de [P_A, P_B]: 0 si y sólo si las preguntas son compatibles."""
    P_a, P_b = np.asarray(P_a, dtype=complex), np.asarray(P_b, dtype=complex)
    return float(np.linalg.norm(P_a @ P_b - P_b @ P_a))


def modelo_qubit(
    theta: float,
    polar: float = np.pi / 3,
    azimut: float = 0.0,
    pureza: float = 1.0,
) -> Conjuntas:
    """Modelo proyectivo en dimensión 2 con proyectores de rango 1.

    P_A = |0⟩⟨0|; P_B = |b⟩⟨b| con |b⟩ = (cos θ/2, sin θ/2). El ángulo θ fija
    el grado de no conmutatividad: ‖[P_A, P_B]‖ = |sin θ|/√2, nulo en θ = 0 y π.
    El estado tiene vector de Bloch pureza·(sin polar·cos azimut,
    sin polar·sin azimut, cos polar); pureza = 1 es un estado puro.
    """
    if not all(np.isfinite(x) for x in (theta, polar, azimut, pureza)):
        raise ValueError("Los parámetros deben ser finitos.")
    if not 0.0 <= pureza <= 1.0:
        raise ValueError("pureza debe estar en [0, 1].")
    r = pureza * np.array([np.sin(polar) * np.cos(azimut), np.sin(polar) * np.sin(azimut), np.cos(polar)])
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    rho = (np.eye(2) + r[0] * sx + r[1] * sy + r[2] * sz) / 2
    b = np.array([np.cos(theta / 2), np.sin(theta / 2)], dtype=complex)
    return probabilidades_proyectivas(rho, proyector(np.array([1, 0])), proyector(b))


def modelo_proyectivo_aleatorio(
    dim: int = 4,
    rango: int = 2,
    no_conmutatividad: float = 1.0,
    seed: Optional[int] = 0,
    mixto: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estado y dos proyectores de rango dado en dimensión arbitraria.

    P_B = U(t) P_A' U(t)†, con U(t) = exp(−i t H), H hermítica aleatoria y
    t = no_conmutatividad. Con t = 0 los dos proyectores son diagonales en la
    misma base y conmutan; al crecer t dejan de conmutar.
    Devuelve (rho, P_A, P_B) para usar con `probabilidades_proyectivas`.
    """
    if dim < 2 or not 1 <= rango < dim:
        raise ValueError("Se requiere dim >= 2 y 1 <= rango < dim.")
    if not np.isfinite(no_conmutatividad):
        raise ValueError("no_conmutatividad debe ser finito.")
    rng = np.random.default_rng(seed)
    P_a = np.diag([1.0] * rango + [0.0] * (dim - rango)).astype(complex)
    # Proyector diagonal distinto de P_A (desplazado), para que t = 0 no sea trivial.
    diag_b = np.roll([1.0] * rango + [0.0] * (dim - rango), 1)
    m = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    H = (m + m.conj().T) / 2
    U = expm(-1j * float(no_conmutatividad) * H)
    P_b = U @ np.diag(diag_b).astype(complex) @ U.conj().T
    P_b = (P_b + P_b.conj().T) / 2
    if mixto:
        g = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
        rho = g @ g.conj().T
        rho = rho / np.trace(rho).real
    else:
        psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
        rho = validar_estado(psi)
    return rho, P_a, P_b


# ──────────────────────── Modelos clásicos ────────────────────────

def modelo_sin_orden(p_conjunta: np.ndarray) -> Conjuntas:
    """Modelo clásico sin efecto de orden.

    Una única distribución conjunta sobre (respuesta a A, respuesta a B),
    indexada [a, b]. El orden sólo cambia cuál se informa primero:
    p_BA[b, a] = p_AB[a, b]. Es el modelo bayesiano conmutativo.
    """
    p = np.asarray(p_conjunta, dtype=float)
    return validar_conjuntas(p, p.T)


def modelo_saturado(p_ab: np.ndarray, p_ba: np.ndarray) -> Conjuntas:
    """Modelo clásico saturado: dos distribuciones conjuntas arbitrarias."""
    return validar_conjuntas(p_ab, p_ba)


def modelo_markov(
    inicial: np.ndarray,
    emision_a: np.ndarray,
    emision_b: np.ndarray,
    transicion_a: np.ndarray,
    transicion_b: np.ndarray,
) -> Conjuntas:
    """Modelo clásico de Markov con estado latente.

    - `inicial[s]`: distribución inicial sobre K estados latentes (la misma
      en ambos órdenes);
    - `emision_x[s]`: P(responder "sí" a la pregunta X | estado s);
    - `transicion_x[r]`: matriz K×K estocástica por columnas que actualiza el
      estado después de responder r a la pregunta X (puede depender de la
      respuesta, lo que incluye el condicionamiento bayesiano y memoria de la
      respuesta dada).

    p_AB[i, j] = Σ_{s,s'} inicial[s]·P(i | s, A)·T_A[i][s', s]·P(j | s', B).
    """
    pi = np.asarray(inicial, dtype=float)
    k = pi.size
    if pi.ndim != 1 or k < 1 or np.any(pi < 0) or not np.isclose(pi.sum(), 1.0):
        raise ValueError("inicial debe ser una distribución sobre los estados latentes.")
    emisiones = []
    for e in (emision_a, emision_b):
        e = np.asarray(e, dtype=float)
        if e.shape != (k,) or np.any(e < 0) or np.any(e > 1) or not np.all(np.isfinite(e)):
            raise ValueError("Cada emisión debe ser un vector de K probabilidades.")
        emisiones.append(np.stack([e, 1.0 - e]))            # [respuesta, estado]
    transiciones = []
    for t in (transicion_a, transicion_b):
        t = np.asarray(t, dtype=float)
        if t.shape != (2, k, k) or np.any(t < 0) or not np.allclose(t.sum(axis=1), 1.0):
            raise ValueError("Cada transición debe tener forma (2, K, K) y columnas que sumen 1.")
        transiciones.append(t)

    def conjunta(e1, t1, e2):
        return np.array([[float(e2[j] @ (t1[i] @ (pi * e1[i]))) for j in range(2)] for i in range(2)])

    return validar_conjuntas(
        conjunta(emisiones[0], transiciones[0], emisiones[1]),
        conjunta(emisiones[1], transiciones[1], emisiones[0]),
    )


def modelo_repeticion(a: float, b: float, kappa_ab: float, kappa_ba: Optional[float] = None) -> Conjuntas:
    """Modelo clásico de repetición (asimilación de la primera respuesta).

    La primera respuesta se extrae de la marginal de su pregunta (a o b). La
    segunda COPIA la primera con probabilidad κ y, si no, se extrae de su
    propia marginal. `kappa_ab` es la probabilidad de copia en el orden A→B
    y `kappa_ba` en B→A (por defecto, igual).

    Resultado analítico: P(respuestas distintas) = (1 − κ)·[a(1−b) + (1−a)b]
    en ambos órdenes, así que q = (κ_BA − κ_AB)·[a(1−b) + (1−a)b].
    Con κ simétrica el modelo cumple QQ EXACTAMENTE y aun así tiene efecto
    de orden: P(B = sí) pasa de b a κ·a + (1−κ)·b. Es un contraejemplo
    clásico a "QQ ⇒ cuántico".
    """
    kappa_ba = kappa_ab if kappa_ba is None else kappa_ba
    for nombre, v in (("a", a), ("b", b), ("kappa_ab", kappa_ab), ("kappa_ba", kappa_ba)):
        if not np.isfinite(v) or not 0.0 <= v <= 1.0:
            raise ValueError(f"{nombre} debe estar en [0, 1].")

    def conjunta(primera, segunda, kappa):
        m1, m2 = np.array([primera, 1 - primera]), np.array([segunda, 1 - segunda])
        return np.array([[m1[i] * (kappa * (i == j) + (1 - kappa) * m2[j]) for j in range(2)] for i in range(2)])

    return validar_conjuntas(conjunta(a, b, kappa_ab), conjunta(b, a, kappa_ba))


def aplicar_ruido_respuesta(
    p_ab: np.ndarray,
    p_ba: np.ndarray,
    eps_primera: float = 0.0,
    eps_segunda: Optional[float] = None,
    eps_segunda_ba: Optional[float] = None,
) -> Conjuntas:
    """Ruido de respuesta: cada respuesta registrada se invierte con probabilidad ε.

    ε depende de la POSICIÓN (primera o segunda). Si es igual en ambos órdenes,
    el residuo se contrae: q' = (1 − 2ε₁)(1 − 2ε₂)·q, de modo que el ruido
    conserva la igualdad QQ (y atenúa una violación). `eps_segunda_ba` permite
    un ruido distinto en el segundo lugar del orden B→A, que sí puede crear
    una violación a partir de datos que la cumplían.
    """
    eps_segunda = eps_primera if eps_segunda is None else eps_segunda
    eps_segunda_ba = eps_segunda if eps_segunda_ba is None else eps_segunda_ba
    for v in (eps_primera, eps_segunda, eps_segunda_ba):
        if not np.isfinite(v) or not 0.0 <= v <= 1.0:
            raise ValueError("Las probabilidades de ruido deben estar en [0, 1].")
    p_ab, p_ba = validar_conjuntas(p_ab, p_ba)

    def canal(eps):
        return np.array([[1 - eps, eps], [eps, 1 - eps]])

    return validar_conjuntas(
        canal(eps_primera) @ p_ab @ canal(eps_segunda),
        canal(eps_primera) @ p_ba @ canal(eps_segunda_ba),
    )


# ─────────────────────── Igualdad QQ: población ───────────────────────

def probabilidad_desacuerdo(p: np.ndarray) -> float:
    """P(las dos respuestas difieren) = p[sí, no] + p[no, sí]."""
    p = np.asarray(p, dtype=float)
    return float(p[0, 1] + p[1, 0])


def residuo_qq(p_ab: np.ndarray, p_ba: np.ndarray) -> float:
    """Residuo poblacional q = [p(AyBn) + p(AnBy)] − [p(ByAn) + p(BnAy)]."""
    return probabilidad_desacuerdo(p_ab) - probabilidad_desacuerdo(p_ba)


def efecto_orden(p_ab: np.ndarray, p_ba: np.ndarray) -> Dict[str, float]:
    """Tamaño del efecto de orden.

    `L1` compara la distribución de los pares (respuesta a A, respuesta a B)
    entre órdenes; `delta_a` y `delta_b` son los cambios en P(sí) de cada
    pregunta al pasar de primera a segunda posición.
    """
    p_ab, p_ba = np.asarray(p_ab, dtype=float), np.asarray(p_ba, dtype=float)
    return {
        "L1": float(np.abs(p_ab - p_ba.T).sum()),
        "delta_a": float(p_ba[:, 0].sum() - p_ab[0, :].sum()),
        "delta_b": float(p_ab[:, 0].sum() - p_ba[0, :].sum()),
    }


def cotas_proyectivas(p_ab: np.ndarray, p_ba: np.ndarray) -> Dict[str, object]:
    """Condiciones necesarias, además de QQ, para que exista un modelo proyectivo.

    Para cada par de respuestas (i a la pregunta A, j a la B) sea
    x_ij = Re⟨ψ|P_A^i P_B^j|ψ⟩. De los observables se obtiene de dos maneras:

        x_ij = p_BA[j, i] − ½·(TP(A_i) − p(A_i))     (orden B→A)
        x_ij = p_AB[i, j] − ½·(TP(B_j) − p(B_j))     (orden A→B)

    donde p(·) es la marginal en primera posición y TP(·) en segunda. Que
    ambas coincidan para los cuatro pares equivale a la igualdad QQ. La
    desigualdad de Cauchy–Schwarz impone además

        x_ij² ≤ p(B_j)·p_AB[i, j]      y      x_ij² ≤ p(A_i)·p_BA[j, i].

    `holgura_minima` < 0 indica una distribución que ningún modelo proyectivo
    puede producir aunque cumpla QQ. Son condiciones necesarias; en la
    exploración numérica de docs/RESULTADOS_S003.md coinciden con la frontera
    de lo alcanzable por modelos de dimensión 4 y 6.
    """
    p_ab, p_ba = validar_conjuntas(p_ab, p_ba)
    p_a, p_b = p_ab.sum(axis=1), p_ba.sum(axis=1)          # marginales en primera posición
    tp_a, tp_b = p_ba.sum(axis=0), p_ab.sum(axis=0)        # marginales en segunda posición
    x_ba = np.array([[p_ba[j, i] - 0.5 * (tp_a[i] - p_a[i]) for j in range(2)] for i in range(2)])
    x_ab = np.array([[p_ab[i, j] - 0.5 * (tp_b[j] - p_b[j]) for j in range(2)] for i in range(2)])
    x = 0.5 * (x_ab + x_ba)
    holguras = np.array([
        [min(p_b[j] * p_ab[i, j] - x[i, j] ** 2, p_a[i] * p_ba[j, i] - x[i, j] ** 2) for j in range(2)]
        for i in range(2)
    ])
    return {
        "x": x,
        "inconsistencia_qq": float(np.abs(x_ab - x_ba).max()),
        "holguras": holguras,
        "holgura_minima": float(holguras.min()),
        "compatible": bool(holguras.min() >= -1e-9 and np.abs(x_ab - x_ba).max() < 1e-9),
    }


def contraste_cotas_proyectivas(
    data: "S003Dataset",
    n_bootstrap: int = 500,
    seed: Optional[int] = 2026,
    alpha: float = 0.05,
) -> Dict[str, object]:
    """Contraste de las cotas proyectivas por bootstrap paramétrico.

    Estima la holgura mínima de `cotas_proyectivas` sobre el ajuste
    restringido a QQ y su intervalo percentil. Si el extremo SUPERIOR del
    intervalo es negativo, los datos son incompatibles con todo modelo
    proyectivo aunque cumplan la igualdad QQ. Un intervalo que incluye
    valores positivos no demuestra compatibilidad.
    """
    if n_bootstrap < 10:
        raise ValueError("n_bootstrap debe ser >= 10.")
    ajuste = ajustar_qq_saturado(data)
    estimada = cotas_proyectivas(*ajuste)["holgura_minima"]
    rng = np.random.default_rng(seed)
    muestras = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        remuestra = S003Dataset(
            rng.multinomial(data.n_ab, ajuste[0].ravel()).reshape(2, 2),
            rng.multinomial(data.n_ba, ajuste[1].ravel()).reshape(2, 2),
        )
        muestras[i] = cotas_proyectivas(*ajustar_qq_saturado(remuestra))["holgura_minima"]
    # Intervalo básico (pivotal): corrige el sesgo del mínimo de varias holguras.
    inferior = 2 * estimada - np.quantile(muestras, 1 - alpha / 2)
    superior = 2 * estimada - np.quantile(muestras, alpha / 2)
    return {
        "holgura_minima": float(estimada),
        "ic": (float(inferior), float(superior)),
        "rechaza_proyectivo": bool(superior < 0),
        "alpha": alpha,
    }


# ─────────────────────── Igualdad QQ: inferencia ───────────────────────

def _wilson(k: np.ndarray, n: np.ndarray, z: float) -> Tuple[np.ndarray, np.ndarray]:
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    mitad = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return centro - mitad, centro + mitad


def _estadisticos_qq(k_ab, n_ab, k_ba, n_ba, alpha: float) -> Dict[str, np.ndarray]:
    """Estadísticos del residuo QQ; admite arreglos para Monte Carlo."""
    k_ab, n_ab, k_ba, n_ba = (np.asarray(x, dtype=float) for x in (k_ab, n_ab, k_ba, n_ba))
    d_ab, d_ba = k_ab / n_ab, k_ba / n_ba
    q = d_ab - d_ba
    comun = (k_ab + k_ba) / (n_ab + n_ba)
    var_h0 = comun * (1 - comun) * (1 / n_ab + 1 / n_ba)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(var_h0 > 0, q / np.sqrt(var_h0), 0.0)
    p_valor = 2 * stats.norm.sf(np.abs(z))
    se = np.sqrt(d_ab * (1 - d_ab) / n_ab + d_ba * (1 - d_ba) / n_ba)
    zc = stats.norm.ppf(1 - alpha / 2)
    l1, u1 = _wilson(k_ab, n_ab, zc)
    l2, u2 = _wilson(k_ba, n_ba, zc)
    return {
        "q": q, "d_ab": d_ab, "d_ba": d_ba, "z": z, "p_valor": p_valor, "error_estandar": se,
        "ic_wald": (q - zc * se, q + zc * se),
        "ic_newcombe": (q - np.sqrt((d_ab - l1) ** 2 + (u2 - d_ba) ** 2), q + np.sqrt((u1 - d_ab) ** 2 + (d_ba - l2) ** 2)),
    }


def contraste_qq(data: S003Dataset, alpha: float = 0.05) -> Dict[str, object]:
    """Contraste de la igualdad QQ sobre datos muestrales.

    Distingue el estimador (`q`), su error estándar, dos intervalos de
    confianza y el tamaño del efecto:

    - `z`, `p_valor`: test z de diferencia de proporciones independientes con
      varianza combinada bajo H0, el propuesto por Wang y Busemeyer (2013);
    - `G`, `p_valor_G`: razón de verosimilitud con 1 grado de libertad;
    - `ic_wald`: q ± z·SE con varianza no combinada;
    - `ic_newcombe`: intervalo híbrido de puntuación (Newcombe, 1998), con
      mejor cobertura en muestras chicas o proporciones extremas;
    - `h_cohen`: 2·asin√d_AB − 2·asin√d_BA.

    Un p-valor alto NO demuestra la igualdad: sólo indica que los datos no
    la contradicen con esta potencia. Para afirmar que |q| es pequeño usar
    `contraste_equivalencia_qq`.
    """
    if not 0 < alpha < 1:
        raise ValueError("alpha debe estar en (0, 1).")
    if data.n_ab < 1 or data.n_ba < 1:
        raise ValueError("Se requiere al menos una observación en cada orden.")
    k_ab = data.counts_ab[0, 1] + data.counts_ab[1, 0]
    k_ba = data.counts_ba[0, 1] + data.counts_ba[1, 0]
    e = _estadisticos_qq(k_ab, data.n_ab, k_ba, data.n_ba, alpha)

    comun = (k_ab + k_ba) / (data.n_ab + data.n_ba)
    g = 0.0
    for k, n in ((k_ab, data.n_ab), (k_ba, data.n_ba)):
        for obs, esp in ((k, n * comun), (n - k, n * (1 - comun))):
            if obs > 0:
                g += 2 * obs * np.log(obs / esp)
    g = max(float(g), 0.0)

    return {
        "q": float(e["q"]),
        "d_ab": float(e["d_ab"]),
        "d_ba": float(e["d_ba"]),
        "error_estandar": float(e["error_estandar"]),
        "z": float(e["z"]),
        "p_valor": float(e["p_valor"]),
        "G": g,
        "p_valor_G": float(stats.chi2.sf(g, 1)),
        "ic_wald": (float(e["ic_wald"][0]), float(e["ic_wald"][1])),
        "ic_newcombe": (float(e["ic_newcombe"][0]), float(e["ic_newcombe"][1])),
        "h_cohen": float(2 * np.arcsin(np.sqrt(e["d_ab"])) - 2 * np.arcsin(np.sqrt(e["d_ba"]))),
        "rechaza_qq": bool(e["p_valor"] < alpha),
        "alpha": alpha,
        "n_ab": data.n_ab,
        "n_ba": data.n_ba,
    }


def contraste_equivalencia_qq(data: S003Dataset, margen: float = 0.05, alpha: float = 0.05) -> Dict[str, object]:
    """Test de equivalencia (TOST) para |q| < margen.

    Es el contraste apropiado para SOSTENER que los datos cumplen QQ dentro
    de una tolerancia: la equivalencia se declara cuando el intervalo de
    confianza de nivel 1 − 2α queda dentro de (−margen, +margen).
    """
    if not 0 < margen < 1:
        raise ValueError("margen debe estar en (0, 1).")
    ic = contraste_qq(data, alpha=2 * alpha)["ic_newcombe"]
    return {
        "ic": ic,
        "margen": margen,
        "alpha": alpha,
        "equivalente": bool(-margen < ic[0] and ic[1] < margen),
    }


def contraste_efecto_orden(data: S003Dataset, alpha: float = 0.05) -> Dict[str, object]:
    """Contraste de homogeneidad: ¿difiere la distribución de pares entre órdenes?

    Compara p_AB[a, b] con p_BA[b, a] mediante la razón de verosimilitud
    (3 grados de libertad). La igualdad QQ sólo es informativa si existe
    efecto de orden: sin él se cumple trivialmente.
    """
    fila_ab = data.counts_ab.ravel().astype(float)
    fila_ba = data.counts_ba.T.ravel().astype(float)
    total = fila_ab + fila_ba
    n = total.sum()
    g = 0.0
    for fila in (fila_ab, fila_ba):
        esperado = total * fila.sum() / n
        mascara = fila > 0
        g += 2 * float(np.sum(fila[mascara] * np.log(fila[mascara] / esperado[mascara])))
    gl = int(np.sum(total > 0)) - 1
    p_valor = float(stats.chi2.sf(max(g, 0.0), gl)) if gl > 0 else 1.0
    return {"G": max(g, 0.0), "grados_libertad": gl, "p_valor": p_valor, "hay_efecto_orden": bool(p_valor < alpha)}


def potencia_qq(d_ab: float, d_ba: float, n_por_orden: int, alpha: float = 0.05) -> float:
    """Potencia asintótica del test z bilateral para detectar q = d_AB − d_BA."""
    for v in (d_ab, d_ba):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Las probabilidades de desacuerdo deben estar en [0, 1].")
    if n_por_orden < 1:
        raise ValueError("n_por_orden debe ser >= 1.")
    q = d_ab - d_ba
    comun = (d_ab + d_ba) / 2
    se0 = np.sqrt(2 * comun * (1 - comun) / n_por_orden)
    se1 = np.sqrt((d_ab * (1 - d_ab) + d_ba * (1 - d_ba)) / n_por_orden)
    if se1 == 0 or se0 == 0:
        return float(q != 0)
    zc = stats.norm.ppf(1 - alpha / 2)
    return float(stats.norm.sf((zc * se0 - q) / se1) + stats.norm.cdf((-zc * se0 - q) / se1))


def n_requerido_qq(d_ab: float, d_ba: float, potencia: float = 0.8, alpha: float = 0.05) -> int:
    """Observaciones por orden necesarias para detectar q con la potencia pedida.

    Es una aproximación normal para dos proporciones independientes. En casos
    degenerados (p1/p2 en {0,1}) la fórmula asintótica puede dar n=0 aunque
    cualquier experimento requiere al menos una observación por orden.
    """
    for nombre, v in (("d_ab", d_ab), ("d_ba", d_ba)):
        if not np.isfinite(v) or not 0.0 <= v <= 1.0:
            raise ValueError(f"{nombre} debe estar en [0, 1].")
    if d_ab == d_ba:
        raise ValueError("Con q = 0 ningún tamaño muestral alcanza potencia mayor que alpha.")
    if not 0 < potencia < 1:
        raise ValueError("potencia debe estar en (0, 1).")
    if not 0 < alpha < 1:
        raise ValueError("alpha debe estar en (0, 1).")
    comun = (d_ab + d_ba) / 2
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(potencia)
    numerador = za * np.sqrt(2 * comun * (1 - comun)) + zb * np.sqrt(d_ab * (1 - d_ab) + d_ba * (1 - d_ba))
    n = int(np.ceil((numerador / (d_ab - d_ba)) ** 2))
    return max(1, n)


def monte_carlo_qq(
    p_ab: np.ndarray,
    p_ba: np.ndarray,
    n_por_orden: int,
    n_replicas: int = 1000,
    seed: Optional[int] = 2026,
    alpha: float = 0.05,
    margen: float = 0.05,
) -> Dict[str, float]:
    """Distribución muestral del residuo QQ para una población dada.

    Devuelve la tasa de rechazo del test z (nivel empírico si q = 0, potencia
    si q ≠ 0), la cobertura de ambos intervalos respecto del q poblacional,
    la tasa de equivalencia declarada (TOST con `margen`) y los momentos del
    estadístico z.
    """
    if n_replicas < 1:
        raise ValueError("n_replicas debe ser >= 1.")
    p_ab, p_ba = validar_conjuntas(p_ab, p_ba)
    rng = np.random.default_rng(seed)
    d_ab, d_ba = probabilidad_desacuerdo(p_ab), probabilidad_desacuerdo(p_ba)
    q_real = d_ab - d_ba
    k_ab = rng.binomial(n_por_orden, d_ab, size=n_replicas)
    k_ba = rng.binomial(n_por_orden, d_ba, size=n_replicas)
    e = _estadisticos_qq(k_ab, n_por_orden, k_ba, n_por_orden, alpha)
    e90 = _estadisticos_qq(k_ab, n_por_orden, k_ba, n_por_orden, 2 * alpha)
    cubre = lambda ic: float(np.mean((ic[0] <= q_real + 1e-12) & (q_real - 1e-12 <= ic[1])))
    return {
        "q_poblacional": float(q_real),
        "n_por_orden": int(n_por_orden),
        "n_replicas": int(n_replicas),
        "q_medio": float(np.mean(e["q"])),
        "q_desvio": float(np.std(e["q"], ddof=1)) if n_replicas > 1 else 0.0,
        "error_estandar_teorico": float(np.sqrt((d_ab * (1 - d_ab) + d_ba * (1 - d_ba)) / n_por_orden)),
        "tasa_rechazo": float(np.mean(e["p_valor"] < alpha)),
        "cobertura_wald": cubre(e["ic_wald"]),
        "cobertura_newcombe": cubre(e["ic_newcombe"]),
        "tasa_equivalencia": float(np.mean((e90["ic_newcombe"][0] > -margen) & (e90["ic_newcombe"][1] < margen))),
        "z_medio": float(np.mean(e["z"])),
        "z_desvio": float(np.std(e["z"], ddof=1)) if n_replicas > 1 else 0.0,
    }


# ─────────────────────── Ajuste de modelos ───────────────────────

MODELOS_S003 = (
    "sin_orden",
    "repeticion_simetrica",
    "qubit_proyectivo",
    "qq_saturado",
    "saturado",
)

# Dimensión de la familia de distribuciones observables de cada modelo (rango
# del jacobiano; ver tests/test_s003_qq.py). El espacio observable tiene 6.
N_PARAMS_S003 = {
    "sin_orden": 3,
    "repeticion_simetrica": 3,
    "qubit_proyectivo": 3,
    "qq_saturado": 5,
    "saturado": 6,
}

# Naturaleza de cada familia. "qq_saturado" es el conjunto de TODAS las
# distribuciones que cumplen QQ: no es ni clásico ni cuántico.
CLASE_S003 = {
    "sin_orden": "clasico",
    "repeticion_simetrica": "clasico",
    "qubit_proyectivo": "proyectivo",
    "qq_saturado": "restriccion_qq",
    "saturado": "clasico",
}

CUMPLE_QQ_S003 = {
    "sin_orden": True,
    "repeticion_simetrica": True,
    "qubit_proyectivo": True,
    "qq_saturado": True,
    "saturado": False,
}

TOLERANCIA_EMPATE_S003 = 1e-3


def _sigmoide(x):
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=float), -40.0, 40.0)))


def _frecuencias(c: np.ndarray, suavizado: float = 0.0) -> np.ndarray:
    c = np.asarray(c, dtype=float) + suavizado
    return c / c.sum() if c.sum() > 0 else np.full(c.shape, 1.0 / c.size)


def log_verosimilitud_s003(data: S003Dataset, pred: Conjuntas, eps: float = 1e-12) -> float:
    """Log-verosimilitud multinomial (sin la constante combinatoria)."""
    return float(
        np.sum(data.counts_ab * np.log(np.clip(pred[0], eps, 1.0)))
        + np.sum(data.counts_ba * np.log(np.clip(pred[1], eps, 1.0)))
    )


def ajustar_sin_orden(data: S003Dataset) -> Conjuntas:
    """Máxima verosimilitud en forma cerrada: se combinan los pares de ambos órdenes."""
    return modelo_sin_orden(_frecuencias(data.counts_ab + data.counts_ba.T))


def ajustar_saturado(data: S003Dataset) -> Conjuntas:
    """Frecuencias observadas de cada orden."""
    return _frecuencias(data.counts_ab), _frecuencias(data.counts_ba)


def ajustar_qq_saturado(data: S003Dataset) -> Conjuntas:
    """Máxima verosimilitud bajo la única restricción d_AB = d_BA (forma cerrada).

    La verosimilitud se factoriza en "acuerdo o desacuerdo" y en el reparto
    dentro de cada grupo; la restricción sólo liga la probabilidad de
    desacuerdo, que se estima combinando los dos órdenes.
    """
    desacuerdo = lambda c: c[0, 1] + c[1, 0]
    n = data.n_ab + data.n_ba
    d = (desacuerdo(data.counts_ab) + desacuerdo(data.counts_ba)) / n if n > 0 else 0.5

    def conjunta(c):
        c = c.astype(float)
        ac, de = c[0, 0] + c[1, 1], c[0, 1] + c[1, 0]
        r_ac = c[0, 0] / ac if ac > 0 else 0.5
        r_de = c[0, 1] / de if de > 0 else 0.5
        return np.array([[(1 - d) * r_ac, d * r_de], [d * (1 - r_de), (1 - d) * (1 - r_ac)]])

    return validar_conjuntas(conjunta(data.counts_ab), conjunta(data.counts_ba))


def _optimizar(objetivo: Callable[[np.ndarray], float], inicios: Iterable[np.ndarray]) -> np.ndarray:
    mejores = []
    for x0 in inicios:
        r = minimize(objetivo, np.asarray(x0, dtype=float), method="L-BFGS-B")
        if np.isfinite(r.fun):
            mejores.append(r)
    if not mejores:
        raise RuntimeError("No fue posible ajustar el modelo.")
    return np.asarray(min(mejores, key=lambda r: r.fun).x, dtype=float)


def _logit(p: float) -> float:
    p = float(np.clip(p, 1e-4, 1 - 1e-4))
    return float(np.log(p / (1 - p)))


def _qubit_desde_parametros(x: np.ndarray) -> Conjuntas:
    """Familia observable del qubit proyectivo, parametrizada sin restricciones.

    Con proyectores de rango 1 en dimensión 2: p(B_j | A_i) = c si i = j y
    1 − c si no, con c = cos²(θ/2), en AMBOS órdenes (ley de reciprocidad).
    Las marginales de la primera respuesta son (1 + r·a)/2 y (1 + r·b)/2 con
    |r| ≤ 1 y ángulo θ entre a y b, lo que restringe los pares alcanzables.
    """
    theta = np.pi * _sigmoide(x[0])
    radio, angulo = _sigmoide(x[1]), x[2]
    p_a = (1 + radio * np.cos(angulo)) / 2
    p_b = (1 + radio * np.cos(angulo - theta)) / 2
    c = np.cos(theta / 2) ** 2

    def conjunta(p):
        return np.array([[p * c, p * (1 - c)], [(1 - p) * (1 - c), (1 - p) * c]])

    return conjunta(p_a), conjunta(p_b)


def ajustar_qubit_proyectivo(data: S003Dataset) -> Conjuntas:
    """Ajusta el modelo proyectivo de dimensión 2 (rango 1), con estado mixto."""
    ab, ba = _frecuencias(data.counts_ab, 0.5), _frecuencias(data.counts_ba, 0.5)
    acuerdo = (data.counts_ab[0, 0] + data.counts_ab[1, 1] + data.counts_ba[0, 0] + data.counts_ba[1, 1] + 1.0) / (data.n_ab + data.n_ba + 2.0)
    theta0 = 2 * np.arccos(np.sqrt(np.clip(acuerdo, 1e-4, 1 - 1e-4)))
    rz = np.clip(2 * ab[0].sum() - 1, -0.999, 0.999)
    inicios = [np.array([_logit(theta0 / np.pi), _logit(max(abs(rz), 0.05)), 0.0 if rz >= 0 else np.pi])]
    for t in (0.2, 0.5, 0.8):
        for ang in (0.0, 1.5, 3.0, 4.5):
            inicios.append(np.array([_logit(t), 1.5, ang]))
    x = _optimizar(lambda z: -log_verosimilitud_s003(data, _qubit_desde_parametros(z)), inicios)
    return validar_conjuntas(*_qubit_desde_parametros(x))


def ajustar_repeticion_simetrica(data: S003Dataset) -> Conjuntas:
    """Ajusta el modelo clásico de repetición con κ igual en ambos órdenes."""
    pred = lambda x: modelo_repeticion(*map(float, _sigmoide(x)))
    a0 = _logit(_frecuencias(data.counts_ab, 0.5)[0].sum())
    b0 = _logit(_frecuencias(data.counts_ba, 0.5)[0].sum())
    inicios = [np.array([a0, b0, k]) for k in (-3.0, -1.0, 0.0, 1.0, 3.0)]
    x = _optimizar(lambda z: -log_verosimilitud_s003(data, pred(z)), inicios)
    return pred(x)


AJUSTADORES_S003: Dict[str, Callable[[S003Dataset], Conjuntas]] = {
    "sin_orden": ajustar_sin_orden,
    "repeticion_simetrica": ajustar_repeticion_simetrica,
    "qubit_proyectivo": ajustar_qubit_proyectivo,
    "qq_saturado": ajustar_qq_saturado,
    "saturado": ajustar_saturado,
}


def ajustar_proyectivo_general(
    data: S003Dataset,
    dim: int = 4,
    rango: int = 2,
    n_inicios: int = 8,
    seed: Optional[int] = 0,
) -> Tuple[Conjuntas, float]:
    """Ajusta un modelo proyectivo de dimensión y rango arbitrarios (estado puro).

    Los parámetros (estado complejo y generador hermítico de la rotación de
    P_B) son muchos más que los observables y no son identificables; sólo
    interesa la distribución ajustada. Devuelve (predicción, log-verosimilitud).
    Se usa en el estudio de identificabilidad, no en la comparación rutinaria.
    """
    if dim < 2 or not 1 <= rango < dim:
        raise ValueError("Se requiere dim >= 2 y 1 <= rango < dim.")
    P_a = np.diag([1.0] * rango + [0.0] * (dim - rango)).astype(complex)
    n_h = dim * dim

    def pred(x):
        psi = x[:dim] + 1j * x[dim:2 * dim]
        if np.linalg.norm(psi) < 1e-9:
            psi = np.ones(dim, dtype=complex)
        m = (x[2 * dim:2 * dim + n_h] + 1j * x[2 * dim + n_h:]).reshape(dim, dim)
        U = expm(-1j * (m + m.conj().T) / 2)
        P_b = U @ P_a @ U.conj().T
        return probabilidades_proyectivas(psi, P_a, (P_b + P_b.conj().T) / 2)

    rng = np.random.default_rng(seed)
    mejor, mejor_ll = None, -np.inf
    for _ in range(n_inicios):
        x0 = rng.normal(size=2 * dim + 2 * n_h)
        r = minimize(lambda z: -log_verosimilitud_s003(data, pred(z)), x0, method="L-BFGS-B")
        if np.isfinite(r.fun) and -r.fun > mejor_ll:
            mejor, mejor_ll = pred(r.x), -float(r.fun)
    if mejor is None:
        raise RuntimeError("No fue posible ajustar el modelo proyectivo general.")
    return mejor, mejor_ll


def dimension_efectiva(prediccion: Callable[[np.ndarray], Conjuntas], puntos: Sequence[np.ndarray], paso: float = 1e-6) -> int:
    """Dimensión de la familia observable: rango máximo del jacobiano numérico."""
    def vector(x):
        p_ab, p_ba = prediccion(np.asarray(x, dtype=float))
        return np.concatenate([np.asarray(p_ab).ravel(), np.asarray(p_ba).ravel()])

    rango = 0
    for x0 in puntos:
        x0 = np.asarray(x0, dtype=float)
        jac = np.zeros((8, x0.size))
        for i in range(x0.size):
            h = np.zeros(x0.size)
            h[i] = paso
            jac[:, i] = (vector(x0 + h) - vector(x0 - h)) / (2 * paso)
        rango = max(rango, int(np.linalg.matrix_rank(jac, tol=1e-5)))
    return rango


# ─────────────────────── Comparación de modelos ───────────────────────

def _js(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    p, q = np.asarray(p, dtype=float).ravel(), np.asarray(q, dtype=float).ravel()
    m = (p + q) / 2
    kl = lambda a, b: float(np.sum(a * np.log((a + eps) / (b + eps))))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def evaluar_modelos_s003(train: S003Dataset, test: S003Dataset) -> Dict[str, Dict[str, float]]:
    """Ajusta cada familia en train y la evalúa en train y en test.

    Por modelo:
    - ajuste: `log_likelihood_train`, `AIC_train`, `BIC_train` (con la
      dimensión efectiva de la familia);
    - predicción: `log_likelihood_test`, `L1_test`, `JS_test`;
    - calibración: `chi2_calibracion` y `p_calibracion`, el estadístico de
      Pearson de los conteos de test frente a la predicción (6 gl);
    - igualdad QQ: `q_modelo`, el residuo de la distribución AJUSTADA (0 por
      construcción en las familias que imponen QQ) y `q_test`, el residuo
      observado en test.

    "El modelo reproduce QQ" (q_modelo = 0) y "el modelo explica mejor los
    datos" (verosimilitud de test, BIC) son afirmaciones distintas.
    """
    n_train = train.n_ab + train.n_ba
    q_test = residuo_qq(_frecuencias(test.counts_ab), _frecuencias(test.counts_ba)) if test.n_ab and test.n_ba else float("nan")
    resultados: Dict[str, Dict[str, float]] = {}
    for nombre in MODELOS_S003:
        pred = AJUSTADORES_S003[nombre](train)
        k = N_PARAMS_S003[nombre]
        ll_train = log_verosimilitud_s003(train, pred)
        obs_ab, obs_ba = _frecuencias(test.counts_ab), _frecuencias(test.counts_ba)
        chi2 = 0.0
        for c, p in ((test.counts_ab, pred[0]), (test.counts_ba, pred[1])):
            esperado = np.clip(p, 1e-12, 1.0) * c.sum()
            chi2 += float(np.sum((c - esperado) ** 2 / esperado)) if c.sum() > 0 else 0.0
        resultados[nombre] = {
            "n_params": k,
            "log_likelihood_train": ll_train,
            "AIC_train": float(2 * k - 2 * ll_train),
            "BIC_train": float(k * np.log(max(n_train, 1)) - 2 * ll_train),
            "log_likelihood_test": log_verosimilitud_s003(test, pred),
            "L1_test": float(0.5 * (np.abs(obs_ab - pred[0]).sum() + np.abs(obs_ba - pred[1]).sum())),
            "JS_test": float(0.5 * (_js(obs_ab, pred[0]) + _js(obs_ba, pred[1]))),
            "chi2_calibracion": chi2,
            "p_calibracion": float(stats.chi2.sf(chi2, 6)),
            "q_modelo": residuo_qq(*pred),
            "q_test": float(q_test),
        }
    return resultados


_CRITERIOS_S003 = {
    "test_log_likelihood": ("log_likelihood_test", True),
    "train_BIC": ("BIC_train", False),
    "train_AIC": ("AIC_train", False),
    "test_L1": ("L1_test", False),
    "test_JS": ("JS_test", False),
}


def modelos_empatados_s003(
    resultados: Dict[str, Dict[str, float]],
    criterio: str = "train_BIC",
    tolerancia: float = TOLERANCIA_EMPATE_S003,
) -> Tuple[str, ...]:
    """Modelos indistinguibles del mejor según el criterio."""
    if criterio not in _CRITERIOS_S003:
        raise ValueError(f"criterio debe ser uno de {tuple(_CRITERIOS_S003)}.")
    if not resultados:
        raise ValueError("resultados no puede estar vacío.")
    clave, mayor = _CRITERIOS_S003[criterio]
    valores = {n: r[clave] for n, r in resultados.items()}
    mejor = max(valores.values()) if mayor else min(valores.values())
    return tuple(n for n, v in valores.items() if abs(v - mejor) <= tolerancia)


def seleccionar_modelo_s003(resultados: Dict[str, Dict[str, float]], criterio: str = "train_BIC") -> str:
    """Primer modelo entre los empatados en el mejor valor del criterio."""
    return modelos_empatados_s003(resultados, criterio)[0]


# ─────────────────────── Regímenes generadores ───────────────────────

REGIMENES_S003 = (
    "sin_orden",
    "repeticion_simetrica",
    "repeticion_incompatible",
    "repeticion_asimetrica",
    "markov_generico",
    "qubit_proyectivo",
    "proyectivo_dim4",
)

# Familia candidata más pequeña que contiene a cada régimen.
MODELO_DE_REGIMEN_S003 = {
    "sin_orden": "sin_orden",
    "repeticion_simetrica": "repeticion_simetrica",
    "repeticion_incompatible": "repeticion_simetrica",
    "repeticion_asimetrica": "saturado",
    "markov_generico": "saturado",
    "qubit_proyectivo": "qubit_proyectivo",
    "proyectivo_dim4": "qq_saturado",
}


def probabilidades_regimen_s003(regimen: str) -> Conjuntas:
    """Probabilidades verdaderas de cada régimen sintético de referencia."""
    if regimen == "sin_orden":
        return modelo_sin_orden(np.array([[0.40, 0.20], [0.10, 0.30]]))
    if regimen == "repeticion_simetrica":
        return modelo_repeticion(0.70, 0.35, 0.40)
    if regimen == "repeticion_incompatible":
        # Clásico, cumple QQ, pero viola las cotas de Cauchy–Schwarz: ningún
        # modelo proyectivo puede generarlo.
        return modelo_repeticion(0.80, 0.25, 0.80)
    if regimen == "repeticion_asimetrica":
        return modelo_repeticion(0.70, 0.35, 0.55, 0.25)
    if regimen == "markov_generico":
        return modelo_markov(
            inicial=[0.4, 0.6],
            emision_a=[0.80, 0.20],
            emision_b=[0.35, 0.50],
            transicion_a=np.array([[[0.8, 0.9], [0.2, 0.1]], [[0.7, 0.3], [0.3, 0.7]]]),
            transicion_b=np.array([[[0.5, 0.7], [0.5, 0.3]], [[0.1, 0.6], [0.9, 0.4]]]),
        )
    if regimen == "qubit_proyectivo":
        return modelo_qubit(theta=np.pi / 3, polar=np.pi / 4, azimut=0.0, pureza=0.9)
    if regimen == "proyectivo_dim4":
        return probabilidades_proyectivas(*modelo_proyectivo_aleatorio(dim=4, rango=2, no_conmutatividad=0.6, seed=11))
    raise ValueError(f"Régimen desconocido: {regimen!r}. Opciones: {REGIMENES_S003}.")


def evaluar_recuperacion_s003(
    regimen: str,
    n_replicas: int = 100,
    n_por_orden: int = 1000,
    seed: int = 2026,
    proporcion_train: float = 0.8,
    alpha: float = 0.05,
) -> Dict[str, object]:
    """Frecuencia con que cada criterio selecciona cada familia, y tasas del test QQ."""
    if regimen not in REGIMENES_S003:
        raise ValueError(f"Régimen desconocido: {regimen!r}.")
    if n_replicas < 1:
        raise ValueError("n_replicas debe ser >= 1.")
    p_ab, p_ba = probabilidades_regimen_s003(regimen)
    verdadero = MODELO_DE_REGIMEN_S003[regimen]
    cuentas = {c: {m: 0 for m in MODELOS_S003} for c in ("train_BIC", "test_log_likelihood")}
    empates = {c: 0 for c in cuentas}
    rechazos_qq = rechazos_orden = 0
    for i in range(n_replicas):
        data = generar_datos_s003(p_ab, p_ba, n_por_orden, seed=seed + i)
        rechazos_qq += contraste_qq(data, alpha)["rechaza_qq"]
        rechazos_orden += contraste_efecto_orden(data, alpha)["hay_efecto_orden"]
        train, test = dividir_train_test_s003(data, proporcion_train, seed=seed + 10000 + i)
        resultados = evaluar_modelos_s003(train, test)
        for criterio in cuentas:
            empatados = modelos_empatados_s003(resultados, criterio)
            cuentas[criterio][empatados[0]] += 1
            empates[criterio] += len(empatados) > 1
    return {
        "regimen": regimen,
        "modelo_verdadero": verdadero,
        "q_poblacional": residuo_qq(p_ab, p_ba),
        "efecto_orden_L1": efecto_orden(p_ab, p_ba)["L1"],
        "n_replicas": n_replicas,
        "n_por_orden": n_por_orden,
        "frecuencia_bic": cuentas["train_BIC"],
        "frecuencia_test": cuentas["test_log_likelihood"],
        "recuperacion_bic": cuentas["train_BIC"][verdadero] / n_replicas,
        "recuperacion_test": cuentas["test_log_likelihood"][verdadero] / n_replicas,
        "empates_bic": empates["train_BIC"],
        "empates_test": empates["test_log_likelihood"],
        "tasa_rechazo_qq": rechazos_qq / n_replicas,
        "tasa_deteccion_orden": rechazos_orden / n_replicas,
    }


def matriz_recuperacion_s003(
    regimenes: Iterable[str] = REGIMENES_S003,
    n_replicas: int = 100,
    n_por_orden: int = 1000,
    seed: int = 2026,
) -> Dict[str, Dict[str, object]]:
    """Matriz régimen generador × modelo seleccionado para todos los regímenes."""
    return {
        regimen: evaluar_recuperacion_s003(regimen, n_replicas, n_por_orden, seed + 100000 * i)
        for i, regimen in enumerate(tuple(regimenes))
    }


if __name__ == "__main__":  # pragma: no cover - resumen ejecutable
    print("S003 — igualdad QQ: regímenes de referencia")
    for nombre in REGIMENES_S003:
        ab, ba = probabilidades_regimen_s003(nombre)
        print(f"  {nombre:<22} q = {residuo_qq(ab, ba):+.4f}   efecto de orden L1 = {efecto_orden(ab, ba)['L1']:.4f}")
    print("\nMatriz de recuperación (BIC), 100 réplicas, n = 1000 por orden")
    for nombre, r in matriz_recuperacion_s003().items():
        print(f"  {nombre:<22} {r['frecuencia_bic']}  rechazo QQ = {r['tasa_rechazo_qq']:.2f}")
