import numpy as np

from saussure_quantum.core import SignoCuanto
from saussure_quantum.experiments_context import (
    distribucion_clasica,
    aplicar_contexto_clasico,
    operador_contexto_diagonal,
    efecto_orden,
    operador_contexto_unitario,
    efecto_orden_no_conmutativo,
)


def test_contexto_clasico_normaliza():
    estado = SignoCuanto(["a", "b", "c"], [1, 1, 1])
    p = aplicar_contexto_clasico(estado, np.array([2.0, 1.0, 1.0]))
    assert np.isclose(p.sum(), 1.0)
    assert p[0] > p[1]


def test_contexto_diagonal_preserva_normalizacion():
    estado = SignoCuanto(["a", "b", "c"], [1, 1j, 1])
    posterior = operador_contexto_diagonal(
        estado, np.array([4.0, 1.0, 0.25])
    )
    assert np.isclose(np.linalg.norm(posterior.amplitudes), 1.0)


def test_contexto_diagonal_equivale_al_baseline_probabilistico():
    estado = SignoCuanto(["a", "b", "c"], [1, 1j, 2])
    pesos = np.array([2.0, 1.0, 3.0])
    q = distribucion_clasica(operador_contexto_diagonal(estado, pesos))
    c = aplicar_contexto_clasico(estado, pesos)
    assert np.allclose(q, c)


def test_efecto_orden_con_filtros_diagonales_es_cero():
    estado = SignoCuanto(["a", "b"], [1, 1])
    resultado = efecto_orden(
        estado,
        np.array([3.0, 1.0]),
        np.array([1.0, 4.0]),
    )
    assert np.isclose(resultado["distancia_L1"], 0.0, atol=1e-12)


def test_contexto_unitario_preserva_norma():
    estado = SignoCuanto(["a", "b"], [1, 1j])
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    posterior = operador_contexto_unitario(estado, X, np.pi / 3)
    assert np.isclose(np.linalg.norm(posterior.amplitudes), 1.0)


def test_contextos_no_conmutativos_producen_efecto_de_orden():
    estado = SignoCuanto(["a", "b"], [1, 1])
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    resultado = efecto_orden_no_conmutativo(
        estado, X, Z, np.pi / 2, np.pi / 2
    )

    assert resultado["norma_conmutador"] > 0
    assert resultado["distancia_L1"] > 0.9
    assert not np.allclose(resultado["AB"], resultado["BA"])


def test_contexto_unitario_con_generador_no_hermitiano_falla():
    estado = SignoCuanto(["a", "b"], [1, 1])
    generador = np.array([[0, 1], [0, 0]], dtype=complex)

    try:
        operador_contexto_unitario(estado, generador)
    except ValueError:
        pass
    else:
        raise AssertionError("Se esperaba rechazar un generador no Hermitiano.")
