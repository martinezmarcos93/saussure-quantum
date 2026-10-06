"""Experimentos de contextualidad semántica.

Este módulo introduce un baseline clásico y un modelo quantum-like mínimo
para estudiar cómo el contexto y el orden de observación modifican un estado
semántico.

No afirma que el significado sea físicamente cuántico.
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from .core import SignoCuanto


def distribucion_clasica(estado: SignoCuanto) -> np.ndarray:
    """Distribución clásica equivalente a |amplitudes|²."""
    return np.abs(estado.amplitudes) ** 2


def aplicar_contexto_clasico(
    estado: SignoCuanto,
    pesos: np.ndarray,
) -> np.ndarray:
    """Actualiza una distribución clásica mediante pesos contextuales."""
    pesos = np.asarray(pesos, dtype=float)
    if pesos.shape != (estado.dimension,):
        raise ValueError("Los pesos deben tener una entrada por significante.")
    if np.any(pesos < 0):
        raise ValueError("Los pesos contextuales no pueden ser negativos.")

    p = distribucion_clasica(estado) * pesos
    total = p.sum()
    if total <= 0:
        raise ValueError("El contexto eliminó toda la masa probabilística.")
    return p / total


def operador_contexto_diagonal(
    estado: SignoCuanto,
    pesos: np.ndarray,
) -> SignoCuanto:
    """Aplica un filtro contextual diagonal y renormaliza el estado."""
    pesos = np.asarray(pesos, dtype=float)
    if pesos.shape != (estado.dimension,):
        raise ValueError("Los pesos deben tener una entrada por significante.")
    if np.any(pesos < 0):
        raise ValueError("Los pesos contextuales no pueden ser negativos.")

    amplitudes = estado.amplitudes * np.sqrt(pesos)
    if np.linalg.norm(amplitudes) <= 1e-15:
        raise ValueError("El operador contextual produjo el estado nulo.")
    return SignoCuanto(estado.significantes.copy(), amplitudes)


def medir_contexto(
    estado: SignoCuanto,
    pesos: np.ndarray,
) -> dict:
    """Aplica un contexto y devuelve el estado posterior y su distribución."""
    posterior = operador_contexto_diagonal(estado, pesos)
    return {
        "estado": posterior,
        "distribucion": distribucion_clasica(posterior),
    }


def efecto_orden(
    estado: SignoCuanto,
    contexto_a: np.ndarray,
    contexto_b: np.ndarray,
) -> dict:
    """Calcula A→B y B→A en un modelo de actualización de estado."""
    ab = operador_contexto_diagonal(
        operador_contexto_diagonal(estado, contexto_a),
        contexto_b,
    )
    ba = operador_contexto_diagonal(
        operador_contexto_diagonal(estado, contexto_b),
        contexto_a,
    )

    return {
        "AB": distribucion_clasica(ab),
        "BA": distribucion_clasica(ba),
        "distancia_L1": float(np.sum(np.abs(
            distribucion_clasica(ab) - distribucion_clasica(ba)
        ))),
    }


def operador_contexto_unitario(
    estado: SignoCuanto,
    generador: np.ndarray,
    intensidad: float = 1.0,
) -> SignoCuanto:
    """Aplica un contexto unitario quantum-like generado por una matriz Hermitiana.

    Esta construcción introduce no conmutatividad de forma controlada. No
    representa una dinámica física del significado; es un formalismo
    experimental para probar si el orden contextual aporta capacidad
    explicativa frente a baselines clásicos.
    """
    generador = np.asarray(generador, dtype=complex)
    if generador.shape != (estado.dimension, estado.dimension):
        raise ValueError("El generador debe ser una matriz cuadrada compatible.")
    if not np.isfinite(intensidad):
        raise ValueError("La intensidad debe ser finita.")
    if not np.allclose(generador, generador.conj().T, atol=1e-10):
        raise ValueError("El generador contextual debe ser Hermitiano.")

    U = expm(-1j * float(intensidad) * generador)
    amplitudes = U @ estado.amplitudes
    return SignoCuanto(estado.significantes.copy(), amplitudes)


def efecto_orden_no_conmutativo(
    estado: SignoCuanto,
    generador_a: np.ndarray,
    generador_b: np.ndarray,
    intensidad_a: float = 1.0,
    intensidad_b: float = 1.0,
) -> dict:
    """Compara A→B y B→A con contextos unitarios potencialmente no conmutativos."""
    a = operador_contexto_unitario(estado, generador_a, intensidad_a)
    ab = operador_contexto_unitario(a, generador_b, intensidad_b)

    b = operador_contexto_unitario(estado, generador_b, intensidad_b)
    ba = operador_contexto_unitario(b, generador_a, intensidad_a)

    commutador = np.asarray(generador_a) @ np.asarray(generador_b) - (
        np.asarray(generador_b) @ np.asarray(generador_a)
    )

    p_ab = distribucion_clasica(ab)
    p_ba = distribucion_clasica(ba)

    return {
        "AB": p_ab,
        "BA": p_ba,
        "distancia_L1": float(np.sum(np.abs(p_ab - p_ba))),
        "norma_conmutador": float(np.linalg.norm(commutador)),
        "estado_AB": ab,
        "estado_BA": ba,
    }
