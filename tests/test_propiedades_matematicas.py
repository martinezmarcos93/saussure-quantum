"""Propiedades matemáticas y casos límite del núcleo.

Cada test comprueba una identidad que puede derivarse a mano; ninguno fija un
valor "porque es lo que devuelve el código".
"""

import warnings

import numpy as np
import pytest

from saussure_quantum.core import SignoCuanto, Langue
from saussure_quantum.collapse import (
    ContextoEnunciativo,
    MedidorParole,
    colapso_parole,
    medicion_debil,
    realidades_alternativas,
)
from saussure_quantum.operators import (
    OperadorDiferencia,
    operador_diferencia,
    operador_diferencia_matriz,
    principio_negatividad,
    similitud_diferencial,
)
from saussure_quantum.uncertainty import (
    ObservablesSaussureanos,
    PrincipioIncertidumbreSaussure,
)
from saussure_quantum.experiments_context import (
    aplicar_contexto_clasico,
    efecto_orden_no_conmutativo,
    operador_contexto_diagonal,
    operador_contexto_unitario,
)


def _estado_aleatorio(d, seed):
    rng = np.random.default_rng(seed)
    return SignoCuanto([f"s{i}" for i in range(d)], rng.normal(size=d) + 1j * rng.normal(size=d))


# ───────────────────────── Estados ─────────────────────────

@pytest.mark.parametrize("d", [1, 2, 3, 7, 50])
def test_estado_puro_es_fisico(d):
    estado = _estado_aleatorio(d, d)
    rho = estado.densidad()
    assert np.isclose(np.linalg.norm(estado.amplitudes), 1.0)
    assert np.isclose(np.trace(rho).real, 1.0)
    assert np.allclose(rho, rho.conj().T)
    assert np.allclose(rho @ rho, rho)
    assert np.linalg.eigvalsh(rho).min() > -1e-12
    assert np.isclose(sum(estado.probabilidad(i) for i in range(d)), 1.0)


@pytest.mark.parametrize("escala", [1e-200, 1e-12, 1.0, 1e12, 1e200])
def test_normalizacion_no_depende_de_la_escala(escala):
    estado = SignoCuanto(["a", "b"], [3 * escala, 4 * escala])
    assert np.allclose(np.abs(estado.amplitudes) ** 2, [9 / 25, 16 / 25])


def test_fase_relativa_e_invariancia_de_fase_global():
    estado = SignoCuanto(["a", "b"], [1, 1j])
    girado = SignoCuanto(["a", "b"], np.array([1, 1j]) * np.exp(1.3j))
    assert np.isclose(estado.fase_relativa(1, 0), np.pi / 2)
    assert np.isclose(girado.fase_relativa(1, 0), np.pi / 2)
    assert np.allclose(estado.densidad(), girado.densidad())


@pytest.mark.parametrize("construir", [
    lambda: SignoCuanto([]),
    lambda: SignoCuanto(["a", "a"]),
    lambda: SignoCuanto(["a", "b"], [0, 0]),
    lambda: SignoCuanto(["a", "b"], [np.nan, 1]),
    lambda: SignoCuanto(["a", "b"], [np.inf, 1]),
    lambda: SignoCuanto(["a", "b"], [1, 1, 1]),
    lambda: SignoCuanto(["a", "b"], [[1, 0], [0, 1]]),
    lambda: SignoCuanto(["a", "b"], [1, 0]).fase_relativa(0, 1),
    lambda: Langue(0),
    lambda: Langue(-2),
    lambda: Langue(2, terminos=["a", "a"]),
    lambda: Langue(3, terminos=["a", "b"]),
])
def test_entradas_degeneradas_lanzan_valueerror(construir):
    with pytest.raises(ValueError):
        construir()


@pytest.mark.parametrize("acceso", [
    lambda: SignoCuanto(["a", "b"]).probabilidad(2),
    lambda: SignoCuanto(["a", "b"], [1, 0]).probabilidad(-1),
    lambda: SignoCuanto(["a", "b"]).colapsar(2),
    lambda: SignoCuanto(["a", "b"]).colapsar(-1),
    lambda: Langue(3).estado_base(3),
    lambda: Langue(3).estado_base(-1),
])
def test_indices_invalidos_no_envuelven_en_silencio(acceso):
    with pytest.raises(IndexError):
        acceso()


def test_base_canonica_es_ortonormal_y_producto_interno_es_hermitico():
    langue = Langue(4)
    base = langue.base_canonica()
    gram = np.array([[langue.producto_interno(a, b) for b in base] for a in base])
    assert np.allclose(gram, np.eye(4))
    psi, phi = langue.superposicion([1, 1j, 2, 0]), langue.superposicion([2, 1, -1j, 1])
    assert np.isclose(langue.producto_interno(psi, phi), np.conj(langue.producto_interno(phi, psi)))


# ───────────────────────── Colapso ─────────────────────────

def test_colapso_es_reproducible_y_no_muta_el_estado():
    estado = SignoCuanto(["a", "b", "c"], [1, 1j, 2])
    original = estado.amplitudes.copy()
    ctx = ContextoEnunciativo(temperatura_semantica=0.7, intencionalidad=[1, 2, 1], ruido_ambiental=0.2)
    primero = colapso_parole(estado, ctx, seed=11)
    segundo = colapso_parole(estado, ctx, seed=11)
    assert primero[0] == segundo[0]
    assert primero[2]["probabilidades_modificadas"] == segundo[2]["probabilidades_modificadas"]
    assert np.array_equal(estado.amplitudes, original)
    assert estado.colapsar(seed=5)[0] == estado.colapsar(seed=5)[0]


def test_frecuencias_de_colapso_convergen_a_la_regla_de_born():
    estado = SignoCuanto(["a", "b", "c"], [1, 1j, 2])
    n = 20000
    conteos = np.bincount(
        [estado.significantes.index(estado.colapsar(seed=i)[0]) for i in range(n)], minlength=3
    )
    p = np.abs(estado.amplitudes) ** 2
    assert np.all(np.abs(conteos / n - p) < 4 * np.sqrt(p * (1 - p) / n))


def test_temperatura_afila_o_aplana_sin_cambiar_el_orden():
    estado = SignoCuanto(["a", "b", "c"], [1, 1, 2])
    base = np.abs(estado.amplitudes) ** 2
    fria = colapso_parole(estado, ContextoEnunciativo(temperatura_semantica=0.5), seed=1)[2]["probabilidades_modificadas"]
    caliente = colapso_parole(estado, ContextoEnunciativo(temperatura_semantica=2.0), seed=1)[2]["probabilidades_modificadas"]
    # p_i^(1/T) normalizado: T=0.5 → p², T=2 → √p.
    assert np.allclose(fria, base**2 / np.sum(base**2))
    assert np.allclose(caliente, np.sqrt(base) / np.sum(np.sqrt(base)))


def test_intencionalidad_incompatible_con_el_estado_falla():
    estado = SignoCuanto(["a", "b"], [1, 0])
    with pytest.raises(ValueError):
        colapso_parole(estado, ContextoEnunciativo(intencionalidad=[0, 1]))
    with pytest.raises(ValueError):
        colapso_parole(SignoCuanto(["a", "b", "c"]), ContextoEnunciativo(intencionalidad=[1, 1]))


@pytest.mark.parametrize("kwargs", [
    {"temperatura_semantica": 0}, {"temperatura_semantica": -1}, {"temperatura_semantica": np.nan},
    {"temperatura_semantica": np.inf}, {"ruido_ambiental": 1.5}, {"ruido_ambiental": -0.1},
    {"intencionalidad": [1, -1]}, {"intencionalidad": [0, 0]}, {"intencionalidad": []},
])
def test_contexto_enunciativo_rechaza_parametros_invalidos(kwargs):
    with pytest.raises(ValueError):
        ContextoEnunciativo(**kwargs)


def test_medicion_debil_es_heuristica_monotona_y_reproducible():
    estado = SignoCuanto(["a", "b", "c"], [3, 2, 1j])
    final_1, _, registro = medicion_debil(estado, fuerza=0.3, n_pasos=30, seed=4)
    final_2, _, _ = medicion_debil(estado, fuerza=0.3, n_pasos=30, seed=4)
    assert final_1 == final_2
    entropias = [r["entropia"] for r in registro]
    assert np.all(np.diff(entropias) <= 1e-12)
    # Los pesos son reales positivos: las fases relativas no cambian.
    ultimas = registro[-1]["amplitudes"]
    assert np.isclose(np.angle(ultimas[2] / ultimas[0]), np.pi / 2)
    # Debe seguir declarada como heurística, no como POVM/Kraus.
    assert "No implementa una medición débil canónica" in medicion_debil.__doc__
    assert "POVM/Kraus" in medicion_debil.__doc__


def test_medicion_debil_fuerza_uno_no_es_colapso_inmediato():
    _, _, registro = medicion_debil(SignoCuanto(["a", "b", "c"], [3, 2, 1]), fuerza=1.0, n_pasos=1, seed=0)
    probs = np.abs(registro[0]["amplitudes"]) ** 2
    p = np.array([9, 4, 1]) / 14
    esperado = p * p**2 / np.sum(p * p**2)  # amplitud·p  →  probabilidad ∝ p³
    assert np.allclose(probs, esperado)
    assert probs.max() < 0.95


@pytest.mark.parametrize("kwargs", [{"fuerza": 1.5}, {"fuerza": -0.1}, {"fuerza": np.nan}, {"n_pasos": -1}, {"n_pasos": 2.5}])
def test_medicion_debil_rechaza_parametros_invalidos(kwargs):
    with pytest.raises(ValueError):
        medicion_debil(SignoCuanto(["a", "b"]), **kwargs)


def test_medidor_y_realidades_son_reproducibles_con_seed():
    estado = SignoCuanto(["a", "b", "c"], [1, 2, 3])
    assert MedidorParole().medir_multiples(estado, 200, seed=3) == MedidorParole().medir_multiples(estado, 200, seed=3)
    assert MedidorParole().medir(estado, seed=8)[0] == MedidorParole().medir(estado, seed=8)[0]
    assert realidades_alternativas(estado, 5, seed=2) == realidades_alternativas(estado, 5, seed=2)


# ───────────────────────── Operadores ─────────────────────────

@pytest.mark.parametrize("d", [1, 2, 3, 5, 8])
def test_matriz_diferencia_es_el_laplaciano_del_grafo_completo(d):
    D = operador_diferencia_matriz(Langue(d))
    u = np.ones(d) / np.sqrt(d)
    psi = _estado_aleatorio(d, 100 + d).amplitudes
    assert np.allclose(D, D.conj().T)
    assert np.allclose(D, d * (np.eye(d) - np.outer(u, u)))
    assert np.allclose(D @ psi, [sum(psi[i] - psi[j] for j in range(d)) for i in range(d)])
    assert np.allclose(np.sort(np.linalg.eigvalsh(D)), [0.0] + [float(d)] * (d - 1))
    # La derivación antigua (D ψ = d ψ − Σ_j |e_j⟩⟨e_j|ψ⟩ = (d−1) ψ) es falsa.
    if d > 1:
        assert not np.allclose(D @ psi, (d - 1) * psi)


@pytest.mark.parametrize("d", [2, 3, 6])
def test_valor_esperado_diferencia_mide_distancia_al_estado_uniforme(d):
    op = OperadorDiferencia(Langue(d))
    etiquetas = [f"término_{i}" for i in range(d)]
    estado = SignoCuanto(etiquetas, _estado_aleatorio(d, 7).amplitudes)
    u = np.ones(d) / np.sqrt(d)
    assert np.isclose(op.valor_esperado(estado), d * (1 - abs(np.vdot(u, estado.amplitudes)) ** 2))
    assert np.isclose(op.valor_esperado(Langue(d).estado_base(0)), d - 1)
    assert np.isclose(op.valor_esperado(SignoCuanto(etiquetas)), 0.0, atol=1e-12)
    with pytest.raises(ValueError):
        op.aplicar(SignoCuanto(etiquetas))  # núcleo de D̂


def test_medir_diferencia_usa_la_regla_de_luders_en_el_autoespacio_degenerado():
    d = 3
    op = OperadorDiferencia(Langue(d))
    estado = Langue(d).estado_base(0)
    u = np.ones(d) / np.sqrt(d)
    esperado = estado.amplitudes - u * np.vdot(u, estado.amplitudes)
    esperado /= np.linalg.norm(esperado)
    valores = []
    for seed in range(400):
        valor, posterior = op.medir_diferencia(estado, seed=seed)
        valores.append(valor)
        if np.isclose(valor, d):
            assert np.isclose(abs(np.vdot(esperado, posterior.amplitudes)), 1.0)
        else:
            assert np.isclose(valor, 0.0)
            assert np.isclose(abs(np.vdot(u, posterior.amplitudes)), 1.0)
    # P(autovalor 0) = |⟨u|ψ⟩|² = 1/d.
    assert abs(np.mean(np.isclose(valores, 0.0)) - 1 / d) < 4 * np.sqrt((1 / d) * (1 - 1 / d) / 400)
    assert op.medir_diferencia(estado, seed=9)[0] == op.medir_diferencia(estado, seed=9)[0]
    with pytest.raises(ValueError):
        op.medir_diferencia(SignoCuanto(["a", "b"]))


def test_diferencia_por_pares_no_equivale_al_operador_matricial():
    etiquetas = ["término_0", "término_1", "término_2"]
    a, b, c = (SignoCuanto(etiquetas, v) for v in np.eye(3))
    originales = [x.amplitudes.copy() for x in (a, b, c)]
    por_pares = operador_diferencia([a, b, c])
    # Σ_{i<j}(ψ_i − ψ_j) = 2ψ_0 + 0·ψ_1 − 2ψ_2: el estado central no influye…
    assert np.allclose(por_pares.amplitudes, np.array([1, 0, -1]) / np.sqrt(2))
    # …y el resultado depende del orden de la lista.
    assert not np.allclose(por_pares.amplitudes, operador_diferencia([b, a, c]).amplitudes)
    assert all(np.array_equal(x.amplitudes, o) for x, o in zip((a, b, c), originales))
    # El operador matricial actúa sobre UN estado y da otra cosa.
    matricial = OperadorDiferencia(Langue(3)).aplicar(a)
    assert np.allclose(matricial.amplitudes, np.array([2, -1, -1]) / np.sqrt(6))
    assert not np.isclose(abs(np.vdot(matricial.amplitudes, por_pares.amplitudes)), 1.0)
    with pytest.raises(ValueError):
        operador_diferencia([a, a])
    with pytest.raises(ValueError):
        operador_diferencia([a])


def test_similitud_y_negatividad():
    a, b = SignoCuanto(["x", "y"], [1, 1j]), SignoCuanto(["x", "y"], [1, -1j])
    assert np.isclose(similitud_diferencial(a, a), 1.0)
    assert np.isclose(similitud_diferencial(a, b), 0.0)
    assert np.isclose(similitud_diferencial(a, SignoCuanto(["x", "y"], np.array([1, 1j]) * 1j)), 1.0)
    for d, seed in [(2, 1), (3, 2), (6, 3)]:
        assert np.isclose(principio_negatividad(_estado_aleatorio(d, seed))["negatividad_total"], d - 1)


# ───────────────────────── Incertidumbre ─────────────────────────

@pytest.mark.parametrize("d", [1, 2, 3, 4, 5, 8, 16])
def test_observables_son_hermiticos_y_el_conmutador_tiene_traza_nula(d):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        obs = ObservablesSaussureanos(d)
    assert np.allclose(obs.S, obs.S.conj().T)
    assert np.allclose(obs.P, obs.P.conj().T)
    # Tr[S,P] = 0 siempre: por eso [S,P] = iℏI es imposible en dimensión finita.
    assert np.isclose(np.trace(obs._conmutador), 0.0)
    assert not obs.verificar_conmutacion()
    assert obs.error_conmutacion() > 0


def test_paradigma_es_nulo_y_avisa_en_dimension_menor_que_tres():
    for d in (1, 2):
        with pytest.warns(RuntimeWarning):
            obs = ObservablesSaussureanos(d)
        assert np.allclose(obs.P, 0.0)


@pytest.mark.parametrize("d", [3, 4, 5, 8])
def test_ondas_planas_son_autovectores_del_paradigma(d):
    obs = ObservablesSaussureanos(d)
    for k in range(d):
        onda = np.exp(2j * np.pi * k * np.arange(d) / d) / np.sqrt(d)
        assert np.allclose(obs.P @ onda, obs.hbar * np.sin(2 * np.pi * k / d) * onda)


@pytest.mark.parametrize("d", [3, 4, 5, 8, 16])
def test_desigualdad_de_robertson(d):
    obs = ObservablesSaussureanos(d)
    rng = np.random.default_rng(d)
    vectores = (
        list(np.eye(d))
        + [np.exp(2j * np.pi * k * np.arange(d) / d) for k in range(d)]
        + [rng.normal(size=d) + 1j * rng.normal(size=d) for _ in range(300)]
        + [rng.normal(size=d) for _ in range(100)]
    )
    for v in vectores:
        estado = SignoCuanto([f"s{i}" for i in range(d)], v)
        _, _, producto = obs.incertidumbre(estado)
        cota = 0.5 * abs(np.vdot(estado.amplitudes, obs._conmutador @ estado.amplitudes))
        assert producto >= cota - 1e-10


def test_no_existe_cota_canonica_hbar_medios_en_dimension_finita():
    d = 10
    obs = ObservablesSaussureanos(d)
    base = Langue(d).estado_base(0)
    delta_s, delta_p, producto = obs.incertidumbre(base)
    assert np.isclose(delta_s, 0.0)
    assert np.isclose(delta_p, obs.hbar / np.sqrt(2))
    assert np.isclose(producto, 0.0)  # < ℏ/2
    onda = SignoCuanto([f"s{i}" for i in range(d)], np.ones(d))
    delta_s, delta_p, _ = obs.incertidumbre(onda)
    assert np.isclose(delta_p, 0.0, atol=1e-10)
    assert np.isclose(delta_s, np.sqrt((d**2 - 1) / 12))


def test_observables_compatibles_tienen_cota_nula():
    obs = ObservablesSaussureanos(5)
    S2 = obs.S @ obs.S
    assert np.allclose(obs.S @ S2 - S2 @ obs.S, 0.0)


@pytest.mark.parametrize("d", [3, 4, 5, 7])
def test_wigner_discreta_es_real_normalizada_y_tiene_marginal_en_x(d):
    principio = PrincipioIncertidumbreSaussure(Langue(d))
    estado = SignoCuanto(principio.langue._base, _estado_aleatorio(d, 40 + d).amplitudes)
    W = principio.visualizar_espacio_fase(estado)
    assert np.isclose(W.sum(), 1.0)
    assert np.allclose(W.sum(axis=1), np.abs(estado.amplitudes) ** 2)
    if d % 2 == 1:
        momento = np.abs(np.fft.fft(estado.amplitudes) / np.sqrt(d)) ** 2
        assert np.allclose(W.sum(axis=0), momento)


# ───────────────────────── S001 ─────────────────────────

def test_contexto_diagonal_equivale_al_baseline_clasico_y_conmuta():
    rng = np.random.default_rng(1)
    for _ in range(200):
        d = int(rng.integers(2, 8))
        estado = _estado_aleatorio(d, int(rng.integers(0, 10**6)))
        w1, w2 = rng.uniform(0.1, 5, d), rng.uniform(0.1, 5, d)
        cuantico = np.abs(operador_contexto_diagonal(estado, w1).amplitudes) ** 2
        assert np.allclose(cuantico, aplicar_contexto_clasico(estado, w1))
        ab = operador_contexto_diagonal(operador_contexto_diagonal(estado, w1), w2)
        ba = operador_contexto_diagonal(operador_contexto_diagonal(estado, w2), w1)
        assert np.allclose(np.abs(ab.amplitudes) ** 2, np.abs(ba.amplitudes) ** 2)


def test_no_conmutatividad_no_garantiza_efecto_de_orden_observable():
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    assert not np.allclose(X @ Z, Z @ X)
    en_mas = efecto_orden_no_conmutativo(SignoCuanto(["a", "b"], [1, 1]), X, Z, np.pi / 4, np.pi / 4)
    assert np.allclose(en_mas["AB"], [0.5, 0.5]) and np.allclose(en_mas["BA"], [1.0, 0.0])
    # Mismo par de operadores, otro estado: el efecto observable desaparece.
    en_cero = efecto_orden_no_conmutativo(SignoCuanto(["a", "b"], [1, 0]), X, Z, np.pi / 4, np.pi / 4)
    assert en_cero["norma_conmutador"] > 0
    assert np.isclose(en_cero["distancia_L1"], 0.0, atol=1e-12)
    conmutan = efecto_orden_no_conmutativo(SignoCuanto(["a", "b"], [1, 1j]), Z, 2 * Z, 0.3, 0.7)
    assert np.isclose(conmutan["distancia_L1"], 0.0, atol=1e-12)


@pytest.mark.parametrize("pesos", [[np.nan, 1, 1], [np.inf, 1, 1], [1, -1, 1], [0, 0, 0], [1, 1]])
def test_pesos_contextuales_invalidos(pesos):
    estado = SignoCuanto(["a", "b", "c"], [1, 1j, 2])
    with pytest.raises(ValueError):
        aplicar_contexto_clasico(estado, pesos)
    with pytest.raises(ValueError):
        operador_contexto_diagonal(estado, pesos)


def test_contexto_unitario_preserva_norma_y_valida_el_generador():
    estado = _estado_aleatorio(3, 5)
    rng = np.random.default_rng(0)
    m = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    posterior = operador_contexto_unitario(estado, m + m.conj().T, 0.7)
    assert np.isclose(np.linalg.norm(posterior.amplitudes), 1.0)
    for generador in (m, np.eye(2), np.array([[np.nan, 0, 0], [0, 1, 0], [0, 0, 1]])):
        with pytest.raises(ValueError):
            operador_contexto_unitario(estado, generador)
    with pytest.raises(ValueError):
        operador_contexto_unitario(estado, np.eye(3), np.inf)
