"""Experimentos de contextualidad semántica.

Este módulo introduce un baseline clásico y un modelo quantum-like mínimo
para estudiar cómo el contexto y el orden de observación modifican un estado
semántico.

No afirma que el significado sea físicamente cuántico.
"""

from __future__ import annotations

import numpy as np

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
