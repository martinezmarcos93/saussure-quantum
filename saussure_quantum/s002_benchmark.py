"""Benchmark S002: comparación de modelos para efecto de orden.

Genera datos sintéticos con una dinámica contextual secuencial conocida y
compara cuatro familias:
1. clásico estático;
2. clásico secuencial;
3. vectorial unitario con operadores potencialmente no conmutativos;
4. quantum-like equivalente al modelo unitario.

El benchmark es metodológico: un resultado favorable al modelo quantum-like
sólo es relevante si mejora ajuste/predicción fuera de muestra bajo una
penalización de complejidad razonable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

import numpy as np


@dataclass(frozen=True)
class S002Dataset:
    """Observaciones agrupadas por orden contextual."""

    counts_ab: np.ndarray
    counts_ba: np.ndarray

    @property
    def n_ab(self) -> int:
        return int(self.counts_ab.sum())

    @property
    def n_ba(self) -> int:
        return int(self.counts_ba.sum())


def _softmax(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    z = x - np.max(x)
    p = np.exp(z)
    return p / p.sum()


def generar_datos_s002(
    n_por_orden: int = 2000,
    seed: int = 2026,
    prob_ab: Iterable[float] = (0.80, 0.20),
    prob_ba: Iterable[float] = (0.20, 0.80),
) -> S002Dataset:
    """Genera un dataset binario con efecto de orden controlado."""
    if n_por_orden < 1:
        raise ValueError("n_por_orden debe ser >= 1.")
    p_ab = np.asarray(tuple(prob_ab), dtype=float)
    p_ba = np.asarray(tuple(prob_ba), dtype=float)
    for p in (p_ab, p_ba):
        if p.shape != (2,) or np.any(p < 0) or not np.isclose(p.sum(), 1):
            raise ValueError("Cada distribución debe tener dos probabilidades que sumen 1.")
    rng = np.random.default_rng(seed)
    return S002Dataset(
        rng.multinomial(n_por_orden, p_ab),
        rng.multinomial(n_por_orden, p_ba),
    )


def distribuciones_observadas(data: S002Dataset) -> Dict[str, np.ndarray]:
    """Devuelve las frecuencias empíricas por orden."""
    return {
        "AB": data.counts_ab / data.n_ab,
        "BA": data.counts_ba / data.n_ba,
    }


def distancia_l1(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.abs(np.asarray(p) - np.asarray(q)).sum())


def divergencia_kl(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    return float(np.sum(p * np.log((p + eps) / (q + eps))))


def divergencia_js(p: np.ndarray, q: np.ndarray) -> float:
    m = (np.asarray(p) + np.asarray(q)) / 2
    return 0.5 * divergencia_kl(p, m) + 0.5 * divergencia_kl(q, m)


def log_likelihood_multinomial(
    counts: np.ndarray,
    probabilities: np.ndarray,
    eps: float = 1e-12,
) -> float:
    """Log-verosimilitud multinomial ignorando la constante combinatoria."""
    counts = np.asarray(counts, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    return float(np.sum(counts * np.log(np.clip(probabilities, eps, 1))))


def aic(log_likelihood: float, n_params: int) -> float:
    return float(2 * n_params - 2 * log_likelihood)


def bic(log_likelihood: float, n_params: int, n_obs: int) -> float:
    return float(n_params * np.log(n_obs) - 2 * log_likelihood)


def evaluar_predicciones(
    data: S002Dataset,
    predicciones: Dict[str, Tuple[np.ndarray, np.ndarray]],
    n_params: Dict[str, int],
) -> Dict[str, Dict[str, float]]:
    """Calcula métricas homogéneas para cada modelo."""
    obs = distribuciones_observadas(data)
    resultados: Dict[str, Dict[str, float]] = {}

    for nombre, (p_ab, p_ba) in predicciones.items():
        ll = (
            log_likelihood_multinomial(data.counts_ab, p_ab)
            + log_likelihood_multinomial(data.counts_ba, p_ba)
        )
        l1 = 0.5 * (distancia_l1(obs["AB"], p_ab) + distancia_l1(obs["BA"], p_ba))
        js = 0.5 * (divergencia_js(obs["AB"], p_ab) + divergencia_js(obs["BA"], p_ba))
        resultados[nombre] = {
            "L1_medio": l1,
            "JS_medio": js,
            "log_likelihood": ll,
            "AIC": aic(ll, n_params[nombre]),
            "BIC": bic(ll, n_params[nombre], data.n_ab + data.n_ba),
        }
    return resultados


def baseline_clasico_estatico(
    p: Iterable[float] = (0.5, 0.5),
) -> Tuple[np.ndarray, np.ndarray]:
    """Un único estado probabilístico para ambos órdenes."""
    p = np.asarray(tuple(p), dtype=float)
    if p.shape != (2,) or np.any(p < 0) or not np.isclose(p.sum(), 1):
        raise ValueError("p debe ser una distribución binaria.")
    return p.copy(), p.copy()


def modelo_clasico_secuencial(
    p0: Iterable[float] = (0.5, 0.5),
    matriz_a: np.ndarray | None = None,
    matriz_b: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo clásico dinámico: cada contexto es una transformación estocástica.

    Las matrices son canales de Markov por columnas: p' = M @ p.
    """
    p0 = np.asarray(tuple(p0), dtype=float)
    if matriz_a is None:
        matriz_a = np.array([[0.9, 0.2], [0.1, 0.8]])
    if matriz_b is None:
        matriz_b = np.array([[0.7, 0.1], [0.3, 0.9]])
    for m in (matriz_a, matriz_b):
        if m.shape != (2, 2) or np.any(m < 0) or not np.allclose(m.sum(axis=0), 1):
            raise ValueError("Los canales clásicos deben ser matrices estocásticas por columnas.")
    return matriz_b @ matriz_a @ p0, matriz_a @ matriz_b @ p0


def modelo_vectorial_unitario(
    amplitud_inicial: Iterable[complex] = (1 / np.sqrt(2), 1 / np.sqrt(2)),
    generador_a: np.ndarray | None = None,
    generador_b: np.ndarray | None = None,
    theta_a: float = np.pi / 2,
    theta_b: float = np.pi / 2,
) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo vectorial unitario; conserva fases pero no usa la semántica de rho."""
    from scipy.linalg import expm

    psi = np.asarray(tuple(amplitud_inicial), dtype=complex)
    if psi.shape != (2,) or not np.isclose(np.linalg.norm(psi), 1):
        raise ValueError("La amplitud inicial debe ser un vector binario normalizado.")
    if generador_a is None:
        generador_a = np.array([[0, 1], [1, 0]], dtype=complex)
    if generador_b is None:
        generador_b = np.array([[1, 0], [0, -1]], dtype=complex)
    for g in (generador_a, generador_b):
        if g.shape != (2, 2) or not np.allclose(g, g.conj().T):
            raise ValueError("Los generadores deben ser Hermitianos.")
    ua = expm(-1j * theta_a * generador_a)
    ub = expm(-1j * theta_b * generador_b)
    p_ab = np.abs(ub @ ua @ psi) ** 2
    p_ba = np.abs(ua @ ub @ psi) ** 2
    return p_ab, p_ba


def modelo_quantum_like(
    *args,
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    """Alias explícito del modelo vectorial para separar capas conceptuales."""
    return modelo_vectorial_unitario(*args, **kwargs)


def benchmark_s002(
    data: S002Dataset | None = None,
) -> Dict[str, Dict[str, float]]:
    """Ejecuta el benchmark con modelos controlados."""
    data = data or generar_datos_s002()
    pred = {
        "clasico_estatico": baseline_clasico_estatico(),
        "clasico_secuencial": modelo_clasico_secuencial(),
        "vectorial_unitario": modelo_vectorial_unitario(),
        "quantum_like": modelo_quantum_like(),
    }
    params = {
        "clasico_estatico": 1,
        "clasico_secuencial": 5,
        "vectorial_unitario": 2,
        "quantum_like": 2,
    }
    return evaluar_predicciones(data, pred, params)
