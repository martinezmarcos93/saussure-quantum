"""S003: respuestas conjuntas e igualdad QQ.

Los tests fijan resultados matemáticos del diseño, incluidos los que limitan
lo que la igualdad QQ puede demostrar: un modelo clásico la cumple, y un
modelo clásico de Markov reproduce cualquier distribución proyectiva.
"""

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.optimize import minimize

from saussure_quantum import s003_qq as s

X = np.array([[0, 1], [1, 0]], dtype=complex)
REFERENCIA = [s.probabilidades_regimen_s003(r) for r in s.REGIMENES_S003]


def _aleatorio(seed, mixto=False):
    rng = np.random.default_rng(seed)
    dim = int(rng.integers(2, 8))
    return s.modelo_proyectivo_aleatorio(dim, int(rng.integers(1, dim)), rng.uniform(0, 3), seed=seed, mixto=mixto)


def _punto_qq(rng):
    d, r = rng.uniform(0.05, 0.95), rng.uniform(0.05, 0.95, 4)
    f = lambda rac, rde: np.array([[(1 - d) * rac, d * rde], [d * (1 - rde), (1 - d) * (1 - rac)]])
    return f(r[0], r[1]), f(r[2], r[3])


# ───────────────────── Modelo proyectivo ─────────────────────

@pytest.mark.parametrize("seed", range(40))
def test_modelo_proyectivo_cumple_qq_en_cualquier_dimension_rango_y_estado(seed):
    for mixto in (False, True):
        rho, pa, pb = _aleatorio(seed, mixto)
        p_ab, p_ba = s.probabilidades_proyectivas(rho, pa, pb)
        for p in (p_ab, p_ba):
            assert np.all(p >= 0) and np.isclose(p.sum(), 1.0)
        assert abs(s.residuo_qq(p_ab, p_ba)) < 1e-12
        cotas = s.cotas_proyectivas(p_ab, p_ba)
        assert cotas["compatible"] and cotas["inconsistencia_qq"] < 1e-12


def test_qq_no_es_trivial_hay_efecto_de_orden():
    efectos = [s.efecto_orden(*s.probabilidades_proyectivas(*_aleatorio(i)))["L1"] for i in range(40)]
    assert max(efectos) > 0.3


def test_proyectores_conmutativos_no_producen_efecto_de_orden():
    rho, pa, pb = s.modelo_proyectivo_aleatorio(5, 2, no_conmutatividad=0.0, seed=3)
    assert np.isclose(s.norma_conmutador(pa, pb), 0.0)
    p_ab, p_ba = s.probabilidades_proyectivas(rho, pa, pb)
    assert np.allclose(p_ab, p_ba.T, atol=1e-12)          # límite clásico
    rho, pa, pb = s.modelo_proyectivo_aleatorio(5, 2, no_conmutatividad=0.8, seed=3)
    assert s.norma_conmutador(pa, pb) > 0.1


@pytest.mark.parametrize("theta", [0.0, 0.5, np.pi / 2, 2.0, np.pi])
def test_no_conmutatividad_del_qubit_es_seno_de_theta(theta):
    pa = s.proyector(np.array([1, 0]))
    pb = s.proyector(np.array([np.cos(theta / 2), np.sin(theta / 2)]))
    assert np.isclose(s.norma_conmutador(pa, pb), abs(np.sin(theta)) / np.sqrt(2), atol=1e-12)
    p_ab, p_ba = s.modelo_qubit(theta, polar=0.9, azimut=0.3, pureza=0.8)
    c = np.cos(theta / 2) ** 2
    # Ley de reciprocidad: P(misma respuesta | primera) = c en ambos órdenes.
    for p in (p_ab, p_ba):
        condicional = p / p.sum(axis=1, keepdims=True)
        assert np.allclose(np.diag(condicional), c, atol=1e-10)


def test_estados_identicos_y_ortogonales_al_proyector():
    pa = s.proyector(np.array([1, 0]))
    pb = s.proyector(np.array([1, 1]))
    en_a, _ = s.probabilidades_proyectivas(np.array([1, 0]), pa, pb)       # autoestado de A
    assert np.allclose(en_a, [[0.5, 0.5], [0.0, 0.0]])
    ortogonal, _ = s.probabilidades_proyectivas(np.array([0, 1]), pa, pb)  # ortogonal a P_A
    assert np.allclose(ortogonal, [[0.0, 0.0], [0.5, 0.5]])
    iguales_ab, iguales_ba = s.probabilidades_proyectivas(np.array([1, 1]), pa, pa)   # A = B
    assert np.allclose(iguales_ab, [[0.5, 0.0], [0.0, 0.5]]) and np.allclose(iguales_ab, iguales_ba)


def test_estado_maximamente_mixto_no_tiene_efecto_en_las_marginales():
    p_ab, p_ba = s.modelo_qubit(1.0, pureza=0.0)
    assert np.allclose(p_ab.sum(axis=1), 0.5) and np.allclose(p_ba.sum(axis=1), 0.5)
    assert abs(s.residuo_qq(p_ab, p_ba)) < 1e-12


def test_invariancia_ante_fase_global_y_cambio_de_base():
    rho, pa, pb = s.modelo_proyectivo_aleatorio(4, 2, 0.7, seed=5)
    referencia = s.probabilidades_proyectivas(rho, pa, pb)
    rng = np.random.default_rng(1)
    m = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    U = expm(-1j * (m + m.conj().T))
    girado = s.probabilidades_proyectivas(U @ rho @ U.conj().T, U @ pa @ U.conj().T, U @ pb @ U.conj().T)
    psi = rng.normal(size=4) + 1j * rng.normal(size=4)
    con_fase = s.probabilidades_proyectivas(psi * np.exp(2.1j), pa, pb)
    sin_fase = s.probabilidades_proyectivas(psi, pa, pb)
    for a, b in zip(referencia + sin_fase, girado + con_fase):
        assert np.allclose(a, b, atol=1e-10)


@pytest.mark.parametrize("estado, pa, pb", [
    (np.array([0, 0]), np.diag([1, 0]), np.diag([1, 0])),
    (np.array([np.nan, 1]), np.diag([1, 0]), np.diag([1, 0])),
    (np.eye(2), np.diag([1, 0]), np.diag([1, 0])),                       # traza 2
    (np.diag([1.5, -0.5]), np.diag([1, 0]), np.diag([1, 0])),            # no positiva
    (np.array([[0.5, 0.5], [0.0, 0.5]]), np.diag([1, 0]), np.diag([1, 0])),  # no hermítica
    (np.array([1, 0]), np.diag([0.5, 0.5]), np.diag([1, 0])),            # POVM, no proyector
    (np.array([1, 0]), np.array([[0, 1], [0, 0]]), np.diag([1, 0])),     # no hermítico
    (np.array([1, 0]), np.eye(3), np.diag([1, 0])),                      # dimensión
])
def test_estado_y_proyectores_invalidos(estado, pa, pb):
    with pytest.raises(ValueError):
        s.probabilidades_proyectivas(estado, pa, pb)


@pytest.mark.parametrize("llamada", [
    lambda: s.modelo_qubit(1.0, pureza=1.5),
    lambda: s.modelo_qubit(np.nan),
    lambda: s.modelo_proyectivo_aleatorio(2, 2),
    lambda: s.modelo_proyectivo_aleatorio(1, 1),
    lambda: s.modelo_proyectivo_aleatorio(4, 2, np.inf),
    lambda: s.proyector(np.zeros(3)),
    lambda: s.proyector(np.array([[1, 2], [1, 2]])),
])
def test_constructores_proyectivos_rechazan_parametros_invalidos(llamada):
    with pytest.raises(ValueError):
        llamada()


def _raiz(e):
    valores, vectores = np.linalg.eigh(e)
    return (vectores * np.sqrt(np.clip(valores, 0, None))) @ vectores.conj().T


def _conjunta_kraus(rho, k1, k2, u=None):
    u = np.eye(rho.shape[0]) if u is None else u
    return np.array([
        [np.trace(k2[j] @ u @ k1[i] @ rho @ k1[i].conj().T @ u.conj().T @ k2[j].conj().T).real for j in range(2)]
        for i in range(2)
    ])


def _hermitica(rng, d):
    m = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    return (m + m.conj().T) / 2


def test_supuestos_de_qq_cuales_son_necesarios():
    """Qué violaciones de los cuatro supuestos rompen la igualdad y cuáles no."""
    rng = np.random.default_rng(0)
    sesgado, povm, unitaria, estados = [], [], [], []
    for i in range(60):
        d = int(rng.integers(2, 5))
        identidad = np.eye(d)
        rho, pa, pb = s.modelo_proyectivo_aleatorio(d, 1, 1.0, seed=i)
        proy_a, proy_b = (pa, identidad - pa), (pb, identidad - pb)

        # (a) Proyectores "borrosos": E = (1−ε)P + ε(I−P), instrumento √E. QQ se conserva.
        ea, eb = rng.uniform(0, 0.4, 2)
        efecto_a, efecto_b = (1 - ea) * pa + ea * (identidad - pa), (1 - eb) * pb + eb * (identidad - pb)
        ka, kb = (_raiz(efecto_a), _raiz(identidad - efecto_a)), (_raiz(efecto_b), _raiz(identidad - efecto_b))
        sesgado.append(abs(s.residuo_qq(_conjunta_kraus(rho, ka, kb), _conjunta_kraus(rho, kb, ka))))

        # (b) POVM genérico (efecto que no es función de un proyector). QQ puede fallar.
        def efecto_generico():
            _, vectores = np.linalg.eigh(_hermitica(rng, d))
            return (vectores * rng.uniform(0, 1, d)) @ vectores.conj().T
        ga, gb = efecto_generico(), efecto_generico()
        ka, kb = (_raiz(ga), _raiz(identidad - ga)), (_raiz(gb), _raiz(identidad - gb))
        povm.append(abs(s.residuo_qq(_conjunta_kraus(rho, ka, kb), _conjunta_kraus(rho, kb, ka))))

        # (c) Dinámica entre las dos preguntas (viola el supuesto 4).
        u = expm(-0.5j * _hermitica(rng, d))
        unitaria.append(abs(s.residuo_qq(_conjunta_kraus(rho, proy_a, proy_b, u), _conjunta_kraus(rho, proy_b, proy_a, u))))

        # (d) Estado inicial distinto en cada orden (viola el supuesto 1).
        otro = rng.normal(size=d) + 1j * rng.normal(size=d)
        estados.append(abs(s.residuo_qq(
            s.probabilidades_proyectivas(rho, pa, pb)[0], s.probabilidades_proyectivas(otro, pa, pb)[1]
        )))

    assert max(sesgado) < 1e-10
    assert max(povm) > 0.01
    assert np.median(unitaria) > 0.05
    assert np.median(estados) > 0.02


# ───────────────────── Modelos clásicos ─────────────────────

def test_modelo_sin_orden_cumple_qq_y_es_compatible_con_un_modelo_proyectivo():
    rng = np.random.default_rng(0)
    for _ in range(200):
        p_ab, p_ba = s.modelo_sin_orden(rng.dirichlet(np.ones(4)).reshape(2, 2))
        assert np.isclose(s.residuo_qq(p_ab, p_ba), 0.0, atol=1e-12)
        assert np.isclose(s.efecto_orden(p_ab, p_ba)["L1"], 0.0, atol=1e-12)
        assert s.cotas_proyectivas(p_ab, p_ba)["compatible"]


def test_repeticion_simetrica_es_clasica_cumple_qq_y_tiene_efecto_de_orden():
    rng = np.random.default_rng(1)
    for _ in range(300):
        a, b, kappa = rng.uniform(0.05, 0.95, 3)
        p_ab, p_ba = s.modelo_repeticion(a, b, kappa)
        assert abs(s.residuo_qq(p_ab, p_ba)) < 1e-12
        # P(B = sí) pasa de b (primera posición) a κ·a + (1−κ)·b (segunda).
        assert np.isclose(p_ab[:, 0].sum(), kappa * a + (1 - kappa) * b)
        assert np.isclose(p_ba[0].sum(), b)
    p_ab, p_ba = s.modelo_repeticion(0.7, 0.35, 0.4)
    assert s.efecto_orden(p_ab, p_ba)["L1"] > 0.25


def test_repeticion_asimetrica_viola_qq_con_la_formula_exacta():
    rng = np.random.default_rng(2)
    for _ in range(300):
        a, b, k1, k2 = rng.uniform(0, 1, 4)
        q = s.residuo_qq(*s.modelo_repeticion(a, b, k1, k2))
        assert np.isclose(q, (k2 - k1) * (a * (1 - b) + (1 - a) * b), atol=1e-12)


def test_existen_distribuciones_clasicas_qq_que_ningun_modelo_proyectivo_genera():
    p_ab, p_ba = s.probabilidades_regimen_s003("repeticion_incompatible")
    assert abs(s.residuo_qq(p_ab, p_ba)) < 1e-12
    cotas = s.cotas_proyectivas(p_ab, p_ba)
    assert cotas["holgura_minima"] < -0.03 and not cotas["compatible"]
    # Confirmación directa: el mejor ajuste proyectivo de dimensión 4 no la alcanza.
    datos = s.S003Dataset(np.round(p_ab * 10**7), np.round(p_ba * 10**7))
    ajuste, _ = s.ajustar_proyectivo_general(datos, dim=4, rango=2, n_inicios=5, seed=0)
    assert max(np.abs(ajuste[0] - p_ab).max(), np.abs(ajuste[1] - p_ba).max()) > 0.02


def test_cotas_proyectivas_delimitan_lo_alcanzable_dentro_del_plano_qq():
    rng = np.random.default_rng(3)
    vistos = {True: 0, False: 0}
    while min(vistos.values()) < 3:
        p_ab, p_ba = _punto_qq(rng)
        holgura = s.cotas_proyectivas(p_ab, p_ba)["holgura_minima"]
        if abs(holgura) < 0.005 or vistos[holgura > 0] >= 3:
            continue
        vistos[holgura > 0] += 1
        datos = s.S003Dataset(np.round(p_ab * 10**7), np.round(p_ba * 10**7))
        ajuste, _ = s.ajustar_proyectivo_general(datos, dim=4, rango=2, n_inicios=6, seed=1)
        error = max(np.abs(ajuste[0] - p_ab).max(), np.abs(ajuste[1] - p_ba).max())
        assert (error < 1e-3) == (holgura > 0)


def _markov_desde(x, k=2):
    x = np.clip(x, -30, 30)
    pi = np.exp(x[:k]); pi /= pi.sum()
    t = np.exp(x[3 * k:].reshape(4, k, k)); t = t / t.sum(axis=1, keepdims=True)
    return s.modelo_markov(pi, s._sigmoide(x[k:2 * k]), s._sigmoide(x[2 * k:3 * k]), t[:2], t[2:])


def test_markov_clasico_de_dos_estados_es_saturado():
    rng = np.random.default_rng(4)
    assert s.dimension_efectiva(_markov_desde, [rng.normal(size=22) for _ in range(4)]) == 6


@pytest.mark.parametrize("regimen", ["qubit_proyectivo", "proyectivo_dim4", "repeticion_simetrica"])
def test_markov_clasico_reproduce_exactamente_las_distribuciones_proyectivas(regimen):
    """Equivalencia observacional: ningún dato de este diseño separa ambas clases."""
    p_ab, p_ba = s.probabilidades_regimen_s003(regimen)
    rng = np.random.default_rng(5)
    objetivo = lambda x: np.sum((_markov_desde(x)[0] - p_ab) ** 2) + np.sum((_markov_desde(x)[1] - p_ba) ** 2)
    mejor = min(
        (minimize(objetivo, rng.normal(size=22), method="L-BFGS-B", options={"maxiter": 5000, "ftol": 1e-16, "gtol": 1e-12}) for _ in range(12)),
        key=lambda r: r.fun,
    )
    ajuste = _markov_desde(mejor.x)
    assert max(np.abs(ajuste[0] - p_ab).max(), np.abs(ajuste[1] - p_ba).max()) < 1e-6


def test_dimensiones_efectivas_de_las_familias():
    rng = np.random.default_rng(6)
    puntos = lambda n: [rng.normal(size=n) for _ in range(4)]
    assert s.dimension_efectiva(s._qubit_desde_parametros, puntos(3)) == s.N_PARAMS_S003["qubit_proyectivo"] == 3
    assert s.dimension_efectiva(lambda x: s.modelo_repeticion(*s._sigmoide(x)), puntos(3)) == s.N_PARAMS_S003["repeticion_simetrica"] == 3

    def proyectivo(x, dim=4, rango=2):
        psi = x[:dim] + 1j * x[dim:2 * dim]
        m = (x[2 * dim:2 * dim + dim * dim] + 1j * x[2 * dim + dim * dim:]).reshape(dim, dim)
        pa = np.diag([1.0] * rango + [0.0] * (dim - rango)).astype(complex)
        u = expm(-1j * (m + m.conj().T) / 2)
        pb = u @ pa @ u.conj().T
        return s.probabilidades_proyectivas(psi, pa, (pb + pb.conj().T) / 2)

    # El modelo proyectivo general tiene la dimensión del plano QQ (5 de 6).
    assert s.dimension_efectiva(proyectivo, puntos(40)) == s.N_PARAMS_S003["qq_saturado"] == 5


def test_modelo_markov_valida_sus_entradas():
    t = np.array([[[1, 0], [0, 1]], [[1, 0], [0, 1]]], dtype=float)
    p_ab, p_ba = s.modelo_markov([0.5, 0.5], [0.9, 0.1], [0.2, 0.8], t, t)
    assert np.isclose(p_ab.sum(), 1.0) and np.all(p_ab >= 0)
    assert np.allclose(p_ab, p_ba.T)      # sin perturbación del estado no hay efecto de orden
    for malos in (
        dict(inicial=[0.5, 0.6]), dict(emision_a=[1.2, 0.1]), dict(emision_b=[0.2]),
        dict(transicion_a=np.ones((2, 2, 2))), dict(inicial=[-0.1, 1.1]),
    ):
        args = dict(inicial=[0.5, 0.5], emision_a=[0.9, 0.1], emision_b=[0.2, 0.8], transicion_a=t, transicion_b=t)
        args.update(malos)
        with pytest.raises(ValueError):
            s.modelo_markov(**args)


# ───────────────────── Ruido ─────────────────────

@pytest.mark.parametrize("e1, e2", [(0.0, 0.0), (0.1, 0.1), (0.05, 0.2), (0.5, 0.1), (1.0, 0.0)])
def test_ruido_de_respuesta_contrae_el_residuo(e1, e2):
    p_ab, p_ba = s.probabilidades_regimen_s003("markov_generico")
    q = s.residuo_qq(p_ab, p_ba)
    q_ruidoso = s.residuo_qq(*s.aplicar_ruido_respuesta(p_ab, p_ba, e1, e2))
    assert np.isclose(q_ruidoso, (1 - 2 * e1) * (1 - 2 * e2) * q, atol=1e-12)
    # En datos que cumplen QQ el ruido simétrico la conserva.
    limpio = s.modelo_qubit(1.0, 0.8)
    assert abs(s.residuo_qq(*s.aplicar_ruido_respuesta(*limpio, e1, e2))) < 1e-12


def test_ruido_maximo_deja_respuestas_al_azar_y_ruido_asimetrico_rompe_qq():
    p_ab, p_ba = s.aplicar_ruido_respuesta(*s.modelo_qubit(1.0, 0.8), 0.5, 0.5)
    assert np.allclose(p_ab, 0.25) and np.allclose(p_ba, 0.25)
    roto = s.aplicar_ruido_respuesta(*s.modelo_qubit(1.0, 0.8), 0.05, 0.05, 0.25)
    assert abs(s.residuo_qq(*roto)) > 0.05
    with pytest.raises(ValueError):
        s.aplicar_ruido_respuesta(*s.modelo_qubit(1.0), 1.5)


# ───────────────────── Datos e inferencia ─────────────────────

def test_datos_reproducibles_y_particion_exacta():
    p_ab, p_ba = REFERENCIA[1]
    a, b, c = (s.generar_datos_s003(p_ab, p_ba, 500, seed=x) for x in (7, 7, 8))
    assert np.array_equal(a.counts_ab, b.counts_ab) and np.array_equal(a.counts_ba, b.counts_ba)
    assert not (np.array_equal(a.counts_ab, c.counts_ab) and np.array_equal(a.counts_ba, c.counts_ba))
    assert a.n_ab == a.n_ba == 500
    for proporcion in (0.5, 0.7, 0.8, 0.9):
        train, test = s.dividir_train_test_s003(a, proporcion, seed=3)
        assert np.array_equal(train.counts_ab + test.counts_ab, a.counts_ab)
        assert np.array_equal(train.counts_ba + test.counts_ba, a.counts_ba)
        assert min(test.counts_ab.min(), test.counts_ba.min()) >= 0


@pytest.mark.parametrize("llamada", [
    lambda: s.generar_datos_s003(REFERENCIA[0][0], REFERENCIA[0][1], 0),
    lambda: s.generar_datos_s003(REFERENCIA[0][0], REFERENCIA[0][1], 2.5),
    lambda: s.generar_datos_s003(np.full((2, 2), 0.3), REFERENCIA[0][1]),
    lambda: s.generar_datos_s003(np.array([[1.2, -0.2], [0, 0]]), REFERENCIA[0][1]),
    lambda: s.generar_datos_s003(np.full(4, 0.25), REFERENCIA[0][1]),
    lambda: s.S003Dataset(np.array([[1, -1], [0, 0]]), np.zeros((2, 2))),
    lambda: s.S003Dataset(np.array([[1.5, 0], [0, 0]]), np.zeros((2, 2))),
    lambda: s.S003Dataset(np.zeros(4), np.zeros((2, 2))),
    lambda: s.dividir_train_test_s003(s.S003Dataset(np.ones((2, 2)), np.ones((2, 2))), 1.0),
    lambda: s.contraste_qq(s.S003Dataset(np.zeros((2, 2)), np.ones((2, 2)))),
    lambda: s.contraste_qq(s.S003Dataset(np.ones((2, 2)), np.ones((2, 2))), alpha=0),
    lambda: s.contraste_equivalencia_qq(s.S003Dataset(np.ones((2, 2)), np.ones((2, 2))), margen=0),
    lambda: s.n_requerido_qq(0.3, 0.3),
    lambda: s.potencia_qq(1.2, 0.3, 100),
])
def test_entradas_invalidas(llamada):
    with pytest.raises(ValueError):
        llamada()


def test_muestras_de_tamano_uno_y_probabilidades_extremas():
    uno = s.S003Dataset(np.array([[1, 0], [0, 0]]), np.array([[0, 0], [0, 1]]))
    r = s.contraste_qq(uno)
    assert r["q"] == 0.0 and r["p_valor"] == 1.0 and np.isfinite(r["z"])
    assert r["ic_newcombe"][0] < 0 < r["ic_newcombe"][1]          # el intervalo no colapsa
    opuestos = s.S003Dataset(np.array([[0, 1], [0, 0]]), np.array([[1, 0], [0, 0]]))
    assert s.contraste_qq(opuestos)["q"] == 1.0
    extremo = s.generar_datos_s003(np.array([[1.0, 0], [0, 0]]), np.array([[0, 0], [0, 1.0]]), 50, seed=1)
    r = s.contraste_qq(extremo)
    assert r["q"] == 0.0 and r["G"] == 0.0 and not r["rechaza_qq"]
    for nombre, ajustar in s.AJUSTADORES_S003.items():
        for p in ajustar(extremo):
            assert np.all(np.isfinite(p)) and np.all(p >= 0) and np.isclose(p.sum(), 1.0), nombre
    assert s.contraste_efecto_orden(extremo)["hay_efecto_orden"]


def test_contraste_qq_distingue_estimador_error_e_intervalo():
    datos = s.S003Dataset(np.array([[300, 200], [100, 400]]), np.array([[350, 150], [250, 250]]))
    r = s.contraste_qq(datos)
    assert np.isclose(r["d_ab"], 0.3) and np.isclose(r["d_ba"], 0.4) and np.isclose(r["q"], -0.1)
    assert np.isclose(r["error_estandar"], np.sqrt(0.3 * 0.7 / 1000 + 0.4 * 0.6 / 1000))
    assert np.isclose(r["z"], -0.1 / np.sqrt(0.35 * 0.65 * 2 / 1000))       # varianza combinada bajo H0
    assert r["ic_wald"][0] < -0.1 < r["ic_wald"][1] < 0 and r["ic_newcombe"][1] < 0
    assert r["rechaza_qq"] and r["p_valor"] < 1e-4 and abs(r["p_valor"] - r["p_valor_G"]) < 1e-4
    assert np.isclose(r["h_cohen"], 2 * np.arcsin(np.sqrt(0.3)) - 2 * np.arcsin(np.sqrt(0.4)))
    assert not s.contraste_equivalencia_qq(datos, margen=0.05)["equivalente"]


def test_no_rechazar_no_equivale_a_demostrar_la_igualdad():
    """Con poca muestra una violación real pasa el test, pero no el de equivalencia."""
    p_ab, p_ba = s.probabilidades_regimen_s003("markov_generico")      # q = 0.105
    no_rechaza = equivalente = 0
    for seed in range(200):
        datos = s.generar_datos_s003(p_ab, p_ba, 100, seed=seed)
        no_rechaza += not s.contraste_qq(datos)["rechaza_qq"]
        equivalente += s.contraste_equivalencia_qq(datos, margen=0.05)["equivalente"]
    assert no_rechaza > 100         # falsos negativos frecuentes con n = 100
    assert equivalente <= 2         # el test de equivalencia no se deja engañar


@pytest.mark.parametrize("regimen, n", [("qubit_proyectivo", 500), ("repeticion_simetrica", 500), ("proyectivo_dim4", 2000)])
def test_nivel_empirico_y_cobertura_bajo_qq(regimen, n):
    p_ab, p_ba = s.probabilidades_regimen_s003(regimen)
    mc = s.monte_carlo_qq(p_ab, p_ba, n, n_replicas=4000, seed=1)
    assert abs(mc["q_poblacional"]) < 1e-12
    assert 0.035 < mc["tasa_rechazo"] < 0.065
    assert 0.935 < mc["cobertura_newcombe"] < 0.965
    assert abs(mc["z_medio"]) < 0.06 and 0.95 < mc["z_desvio"] < 1.05
    assert abs(mc["q_desvio"] - mc["error_estandar_teorico"]) / mc["error_estandar_teorico"] < 0.05


def test_potencia_analitica_coincide_con_monte_carlo_y_crece_con_n():
    p_ab, p_ba = s.probabilidades_regimen_s003("markov_generico")
    d_ab, d_ba = s.probabilidad_desacuerdo(p_ab), s.probabilidad_desacuerdo(p_ba)
    previas = 0.0
    for n in (100, 500, 2500):
        analitica = s.potencia_qq(d_ab, d_ba, n)
        empirica = s.monte_carlo_qq(p_ab, p_ba, n, n_replicas=4000, seed=2)["tasa_rechazo"]
        assert abs(analitica - empirica) < 0.03
        assert analitica > previas
        previas = analitica
    n80 = s.n_requerido_qq(d_ab, d_ba, potencia=0.8)
    assert 0.78 < s.potencia_qq(d_ab, d_ba, n80) < 0.83
    assert np.isclose(s.potencia_qq(0.3, 0.3, 1000), 0.05, atol=1e-6)


def test_contraste_de_cotas_proyectivas():
    """Un régimen clásico pasa QQ al nivel nominal y aun así se detecta como no proyectivo."""
    p_inc = s.probabilidades_regimen_s003("repeticion_incompatible")
    p_com = s.probabilidades_regimen_s003("proyectivo_dim4")
    assert s.monte_carlo_qq(*p_inc, 2000, n_replicas=4000, seed=1)["tasa_rechazo"] < 0.065
    rechazos_inc = rechazos_com = 0
    for seed in range(20):
        rechazos_inc += s.contraste_cotas_proyectivas(s.generar_datos_s003(*p_inc, 2000, seed=seed), 200, seed=seed)["rechaza_proyectivo"]
        rechazos_com += s.contraste_cotas_proyectivas(s.generar_datos_s003(*p_com, 2000, seed=seed), 200, seed=seed)["rechaza_proyectivo"]
    assert rechazos_inc == 20 and rechazos_com <= 1
    with pytest.raises(ValueError):
        s.contraste_cotas_proyectivas(s.generar_datos_s003(*p_com, 100, seed=0), n_bootstrap=2)


def test_contraste_de_efecto_de_orden():
    sin = s.generar_datos_s003(*s.probabilidades_regimen_s003("sin_orden"), 2000, seed=1)
    con = s.generar_datos_s003(*s.probabilidades_regimen_s003("repeticion_simetrica"), 2000, seed=1)
    assert not s.contraste_efecto_orden(sin)["hay_efecto_orden"]
    r = s.contraste_efecto_orden(con)
    assert r["hay_efecto_orden"] and r["grados_libertad"] == 3


# ───────────────────── Ajuste y comparación ─────────────────────

@pytest.mark.parametrize("indice", range(len(s.REGIMENES_S003)))
def test_ajustes_son_validos_anidados_y_respetan_qq(indice):
    datos = s.generar_datos_s003(*REFERENCIA[indice], 3000, seed=indice)
    ll = {}
    for nombre, ajustar in s.AJUSTADORES_S003.items():
        pred = ajustar(datos)
        for p in pred:
            assert np.all(p >= 0) and np.isclose(p.sum(), 1.0)
        if s.CUMPLE_QQ_S003[nombre]:
            assert abs(s.residuo_qq(*pred)) < 1e-8
        ll[nombre] = s.log_verosimilitud_s003(datos, pred)
    # Familias anidadas: sin_orden, repetición y qubit ⊂ plano QQ ⊂ saturado.
    for restringido in ("sin_orden", "repeticion_simetrica", "qubit_proyectivo"):
        assert ll[restringido] <= ll["qq_saturado"] + 1e-6
    assert ll["qq_saturado"] <= ll["saturado"] + 1e-9


def test_ajuste_qq_saturado_es_el_maximo_bajo_la_restriccion():
    datos = s.generar_datos_s003(*s.probabilidades_regimen_s003("markov_generico"), 2000, seed=3)
    cerrado = s.log_verosimilitud_s003(datos, s.ajustar_qq_saturado(datos))
    rng = np.random.default_rng(0)
    for _ in range(300):
        assert s.log_verosimilitud_s003(datos, _punto_qq(rng)) <= cerrado + 1e-9
    # La razón de verosimilitud saturado / QQ es el estadístico G del contraste.
    g = 2 * (s.log_verosimilitud_s003(datos, s.ajustar_saturado(datos)) - cerrado)
    assert np.isclose(g, s.contraste_qq(datos)["G"], atol=1e-8)


@pytest.mark.parametrize("regimen", ["qubit_proyectivo", "repeticion_simetrica", "sin_orden"])
def test_ajuste_recupera_la_distribucion_generadora(regimen):
    p_ab, p_ba = s.probabilidades_regimen_s003(regimen)
    datos = s.S003Dataset(np.round(p_ab * 10**6), np.round(p_ba * 10**6))
    pred = s.AJUSTADORES_S003[s.MODELO_DE_REGIMEN_S003[regimen]](datos)
    assert max(np.abs(pred[0] - p_ab).max(), np.abs(pred[1] - p_ba).max()) < 2e-3


def test_evaluacion_de_modelos_separa_reproducir_qq_de_explicar_los_datos():
    datos = s.generar_datos_s003(*s.probabilidades_regimen_s003("repeticion_simetrica"), 4000, seed=5)
    train, test = s.dividir_train_test_s003(datos, 0.8, seed=5)
    r = s.evaluar_modelos_s003(train, test)
    assert set(r) == set(s.MODELOS_S003)
    for metricas in r.values():
        assert all(np.isfinite(v) for v in metricas.values())
    # El qubit proyectivo reproduce QQ y aun así explica mal estos datos clásicos.
    assert abs(r["qubit_proyectivo"]["q_modelo"]) < 1e-8
    assert r["qubit_proyectivo"]["log_likelihood_test"] < r["repeticion_simetrica"]["log_likelihood_test"] - 5
    assert r["qubit_proyectivo"]["p_calibracion"] < 0.01 < r["repeticion_simetrica"]["p_calibracion"]
    assert s.seleccionar_modelo_s003(r, "train_BIC") == "repeticion_simetrica"
    with pytest.raises(ValueError):
        s.seleccionar_modelo_s003(r, "criterio_inexistente")
    with pytest.raises(ValueError):
        s.modelos_empatados_s003({}, "train_BIC")


def test_recuperacion_es_reproducible_y_tiene_estructura_completa():
    a = s.evaluar_recuperacion_s003("qubit_proyectivo", n_replicas=6, n_por_orden=400, seed=3)
    b = s.evaluar_recuperacion_s003("qubit_proyectivo", n_replicas=6, n_por_orden=400, seed=3)
    assert a == b
    assert sum(a["frecuencia_bic"].values()) == 6 and sum(a["frecuencia_test"].values()) == 6
    assert 0 <= a["tasa_rechazo_qq"] <= 1 and a["modelo_verdadero"] == "qubit_proyectivo"
    with pytest.raises(ValueError):
        s.evaluar_recuperacion_s003("inexistente")
    with pytest.raises(ValueError):
        s.probabilidades_regimen_s003("inexistente")


@pytest.mark.parametrize("regimen", s.REGIMENES_S003)
def test_regimenes_de_referencia(regimen):
    p_ab, p_ba = s.probabilidades_regimen_s003(regimen)
    assert np.isclose(p_ab.sum(), 1.0) and np.isclose(p_ba.sum(), 1.0) and min(p_ab.min(), p_ba.min()) >= 0
    q = s.residuo_qq(p_ab, p_ba)
    if regimen in ("repeticion_asimetrica", "markov_generico"):
        assert abs(q) > 0.1
    else:
        assert abs(q) < 1e-12


# ───────────────────── Identificabilidad ─────────────────────

def _distancia(x, y):
    return max(np.abs(x[0] - y[0]).max(), np.abs(x[1] - y[1]).max())


def test_parametros_proyectivos_no_identificables():
    """Modelos proyectivos distintos con exactamente los mismos observables."""
    # Signo del azimut (fase relativa del estado).
    assert _distancia(s.modelo_qubit(1.0, 0.9, 0.7, 0.8), s.modelo_qubit(1.0, 0.9, -0.7, 0.8)) < 1e-12

    # Pureza frente a componente del vector de Bloch fuera del plano de medición.
    def desde_bloch(r):
        norma = np.linalg.norm(r)
        return s.modelo_qubit(1.0, np.arccos(r[2] / norma), np.arctan2(r[1], r[0]), norma)

    assert _distancia(desde_bloch(np.array([0.3, 0.0, 0.5])), desde_bloch(np.array([0.3, 0.6, 0.5]))) < 1e-12

    # Dimensión y rango: el qubit embebido en dimensión 4 con proyectores de rango 2.
    psi, auxiliar = np.array([np.cos(0.45), np.sin(0.45)]), np.array([0.6, 0.8])
    b = np.array([np.cos(0.5), np.sin(0.5)])
    embebido = s.probabilidades_proyectivas(
        np.kron(psi, auxiliar), np.kron(np.diag([1.0, 0.0]), np.eye(2)), np.kron(np.outer(b, b), np.eye(2))
    )
    assert _distancia(s.modelo_qubit(1.0, 0.9, 0.0, 1.0), embebido) < 1e-12


@pytest.mark.parametrize("kappa", [0.0, 0.2, 0.6, 1.0])
def test_modelo_clasico_y_modelo_proyectivo_con_observables_identicos(kappa):
    """Repetición con a = b = 1/2 ≡ qubit máximamente mixto con cos²(θ/2) = (1+κ)/2."""
    clasico = s.modelo_repeticion(0.5, 0.5, kappa)
    cuantico = s.modelo_qubit(2 * np.arccos(np.sqrt((1 + kappa) / 2)), pureza=0.0)
    assert _distancia(clasico, cuantico) < 1e-12


def test_gran_parte_de_los_modelos_clasicos_qq_tiene_un_gemelo_proyectivo():
    rng = np.random.default_rng(0)
    compatibles = np.mean([
        s.cotas_proyectivas(*s.modelo_repeticion(*rng.uniform(0, 1, 3)))["compatible"] for _ in range(4000)
    ])
    assert 0.5 < compatibles < 0.65
