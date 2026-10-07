"""Identificabilidad del benchmark S002.

Estos tests fijan resultados ANALÍTICOS sobre qué puede y qué no puede
distinguir el diseño (datos binarios, dos órdenes). Varios son resultados
negativos para la hipótesis quantum-like y deben seguir siéndolo mientras el
diseño no cambie.
"""

import numpy as np
import pytest

from saussure_quantum import s002_benchmark as b


def test_modelo_vectorial_predice_ab_uniforme_para_todo_theta():
    for theta_a in np.linspace(-np.pi, np.pi, 17):
        for theta_b in np.linspace(-np.pi, np.pi, 17):
            p_ab, p_ba = b.modelo_vectorial_unitario(theta_a=theta_a, theta_b=theta_b)
            assert np.allclose(p_ab, [0.5, 0.5], atol=1e-12)
            assert np.isclose(p_ba[0], (1 + np.sin(2 * theta_a) * np.sin(2 * theta_b)) / 2, atol=1e-12)


def test_quantum_like_y_vectorial_son_observacionalmente_equivalentes():
    rng = np.random.default_rng(0)
    for _ in range(500):
        theta_a, theta_b, ruido = rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(0, 1)
        p_ab, p_ba = b.modelo_quantum_like(ruido=ruido, theta_a=theta_a, theta_b=theta_b)
        objetivo = (1 - ruido) * np.sin(2 * theta_a) * np.sin(2 * theta_b)
        assert np.allclose(p_ab, [0.5, 0.5], atol=1e-12)
        assert np.isclose(p_ba[0], (1 + objetivo) / 2, atol=1e-12)
        # Existe un modelo vectorial SIN ruido con la misma predicción.
        equivalente = b.modelo_vectorial_unitario(theta_a=np.pi / 4, theta_b=np.arcsin(objetivo) / 2)
        assert np.allclose(equivalente[1], p_ba, atol=1e-10)
    assert b.CLASE_OBSERVACIONAL["quantum_like"] == b.CLASE_OBSERVACIONAL["vectorial_unitario"]


def test_modelo_clasico_secuencial_es_saturado():
    """Canales constantes alcanzan cualquier par (p_AB, p_BA)."""
    rng = np.random.default_rng(1)
    for _ in range(200):
        a, c = rng.uniform(0, 1, 2)
        canal_a = np.array([[1 - a, 1 - a], [a, a]])
        canal_b = np.array([[1 - c, 1 - c], [c, c]])
        p_ab, p_ba = b.modelo_clasico_secuencial(matriz_a=canal_a, matriz_b=canal_b)
        assert np.isclose(p_ab[1], c) and np.isclose(p_ba[1], a)


def test_ajuste_secuencial_alcanza_la_verosimilitud_saturada():
    for seed, prob_ab, prob_ba in [(1, (0.5, 0.5), (0.95, 0.05)), (2, (0.2, 0.8), (0.7, 0.3)), (3, (0.43, 0.57), (0.48, 0.52))]:
        data = b.generar_datos_s002(n_por_orden=800, seed=seed, prob_ab=prob_ab, prob_ba=prob_ba)
        saturada = -(
            b.log_likelihood_multinomial(data.counts_ab, data.counts_ab / data.n_ab)
            + b.log_likelihood_multinomial(data.counts_ba, data.counts_ba / data.n_ba)
        )
        assert np.isclose(b._nll_dataset(data, b.ajustar_clasico_secuencial(data)), saturada, atol=1e-4)


def test_ajustes_unitarios_coinciden_y_no_superan_al_saturado():
    for seed in range(5):
        data = b.generar_datos_s002(n_por_orden=600, seed=seed)
        vectorial = b._nll_dataset(data, b.ajustar_vectorial_unitario(data))
        cuantico = b._nll_dataset(data, b.ajustar_quantum_like(data))
        secuencial = b._nll_dataset(data, b.ajustar_clasico_secuencial(data))
        assert np.isclose(vectorial, cuantico, atol=1e-4)
        assert secuencial <= vectorial + 1e-4


def test_parametros_efectivos_son_el_rango_del_jacobiano():
    def rango(pred, x0):
        x0 = np.asarray(x0, dtype=float)
        base = np.array([pred(x0)[0][0], pred(x0)[1][0]])
        jac = np.zeros((2, len(x0)))
        for i in range(len(x0)):
            paso = np.zeros(len(x0)); paso[i] = 1e-6
            desplazado = np.array([pred(x0 + paso)[0][0], pred(x0 + paso)[1][0]])
            jac[:, i] = (desplazado - base) / 1e-6
        return int(np.linalg.matrix_rank(jac, tol=1e-6))

    def secuencial(x):
        p0, a0, a1, b0, b1 = map(float, b._sigmoid(x))
        p = np.array([1 - p0, p0])
        return b.modelo_clasico_secuencial(p, np.array([[1 - a0, a1], [a0, 1 - a1]]), np.array([[1 - b0, b1], [b0, 1 - b1]]))

    assert rango(lambda x: b.baseline_clasico_estatico((1 - x[0], x[0])), [0.3]) == b.N_PARAMS_EFECTIVOS["clasico_estatico"] == 1
    assert rango(secuencial, [0.2, -0.4, 0.7, 0.1, -0.9]) == b.N_PARAMS_EFECTIVOS["clasico_secuencial"] == 2
    assert rango(lambda x: b.modelo_vectorial_unitario(theta_a=x[0], theta_b=x[1]), [0.3, 0.5]) == b.N_PARAMS_EFECTIVOS["vectorial_unitario"] == 1
    assert rango(lambda x: b.modelo_quantum_like(ruido=x[2], theta_a=x[0], theta_b=x[1]), [0.3, 0.5, 0.2]) == b.N_PARAMS_EFECTIVOS["quantum_like"] == 1


def test_empates_se_informan_en_lugar_de_forzar_un_ganador():
    data = b.generar_datos_s002(n_por_orden=2000, seed=2026)
    resultados = b.benchmark_ajustado_s002(data)
    empatados = b.modelos_empatados_s002(resultados, "test_log_likelihood", tolerancia=1e-3)
    estricto = b.seleccionar_modelo_s002(resultados, "test_log_likelihood")
    assert estricto in empatados
    # Vectorial y quantum-like nunca pueden separarse por verosimilitud.
    assert abs(resultados["vectorial_unitario"]["log_likelihood"] - resultados["quantum_like"]["log_likelihood"]) < 1e-3
    assert ("vectorial_unitario" in empatados) == ("quantum_like" in empatados)
    # Con parámetros efectivos su BIC coincide; con los nominales difiere en ln(n).
    assert np.isclose(resultados["vectorial_unitario"]["BIC_train_efectivo"], resultados["quantum_like"]["BIC_train_efectivo"], atol=1e-3)
    n_train = 0.5 * (resultados["quantum_like"]["BIC_train"] - resultados["vectorial_unitario"]["BIC_train"])
    assert n_train > 0


def test_modelos_empatados_valida_argumentos():
    resultados = {"a": {"log_likelihood": -1.0}, "b": {"log_likelihood": -1.0005}, "c": {"log_likelihood": -3.0}}
    assert b.modelos_empatados_s002(resultados, "test_log_likelihood") == ("a", "b")
    assert b.modelos_empatados_s002(resultados, "test_log_likelihood", tolerancia=0.0) == ("a",)
    with pytest.raises(ValueError):
        b.modelos_empatados_s002({}, "test_log_likelihood")
    with pytest.raises(ValueError):
        b.modelos_empatados_s002(resultados, "criterio_inexistente")
    with pytest.raises(ValueError):
        b.seleccionar_modelo_s002(resultados, "criterio_inexistente")


def test_recuperacion_de_sin_orden_usa_el_modelo_estatico():
    """Antes se buscaba 'sin_orden' entre nombres de modelos: recuperación 0 fija."""
    r = b.evaluar_recuperacion_s002("sin_orden", n_replicas=12, n_por_orden=1000, seed=2026)
    assert r["modelo_verdadero"] == "clasico_estatico"
    assert r["frecuencia_bic"].get("clasico_estatico", 0) == 12
    assert r["recuperacion_bic"] == 1.0
    assert r["recuperacion_test"] == r["frecuencia_test"].get("clasico_estatico", 0) / 12


def test_quantum_like_no_es_recuperable_frente_al_vectorial():
    """Resultado negativo documentado: el régimen quantum-like no se distingue."""
    r = b.evaluar_recuperacion_s002("quantum_like", n_replicas=12, n_por_orden=1000, seed=2026)
    # El BIC nominal elige siempre el vectorial (misma verosimilitud, menos parámetros).
    assert r["recuperacion_bic"] == 0.0
    assert r["frecuencia_bic"] == {"vectorial_unitario": 12}
    # Con parámetros efectivos el empate es exacto en todas las réplicas.
    assert r["empates_bic_efectivo"] == 12
    assert r["recuperacion_clase_bic_efectivo"] == 1.0


def test_recuperacion_es_reproducible():
    args = dict(n_replicas=4, n_por_orden=300, seed=7)
    assert b.evaluar_recuperacion_s002("clasico_secuencial", **args) == b.evaluar_recuperacion_s002("clasico_secuencial", **args)


@pytest.mark.parametrize("proporcion", [0.5, 0.7, 0.8, 0.9])
def test_split_es_una_particion_exacta_y_reproducible(proporcion):
    data = b.generar_datos_s002(n_por_orden=1000, seed=5)
    train, test = b.dividir_train_test(data, proporcion, seed=9)
    otra_vez = b.dividir_train_test(data, proporcion, seed=9)
    assert np.array_equal(train.counts_ab + test.counts_ab, data.counts_ab)
    assert np.array_equal(train.counts_ba + test.counts_ba, data.counts_ba)
    assert min(test.counts_ab.min(), test.counts_ba.min(), train.counts_ab.min(), train.counts_ba.min()) >= 0
    assert np.array_equal(train.counts_ab, otra_vez[0].counts_ab) and np.array_equal(test.counts_ba, otra_vez[1].counts_ba)


def test_semillas_distintas_generan_datos_distintos():
    a, c = b.generar_datos_s002(seed=1), b.generar_datos_s002(seed=2)
    assert not (np.array_equal(a.counts_ab, c.counts_ab) and np.array_equal(a.counts_ba, c.counts_ba))


@pytest.mark.parametrize("regimen", b.REGIMENES_S002)
def test_probabilidades_de_cada_regimen_son_validas(regimen):
    for ruido in (0.0, 0.05, 0.5, 1.0):
        for p in b.probabilidades_regimen_s002(regimen, ruido=ruido):
            assert np.all(np.isfinite(p)) and np.all(p >= 0) and np.isclose(p.sum(), 1.0)


def test_ruido_uno_borra_el_efecto_de_orden_del_modelo_quantum_like():
    p_ab, p_ba = b.modelo_quantum_like(ruido=1.0)
    assert np.allclose(p_ab, [0.5, 0.5]) and np.allclose(p_ba, [0.5, 0.5])
    with pytest.raises(ValueError):
        b.modelo_quantum_like(ruido=1.5)
