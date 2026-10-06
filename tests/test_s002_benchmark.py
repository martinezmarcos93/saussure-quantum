import numpy as np

from saussure_quantum.s002_benchmark import (
    S002Dataset,
    generar_datos_s002,
    baseline_clasico_estatico,
    modelo_clasico_secuencial,
    modelo_vectorial_unitario,
    modelo_quantum_like,
    benchmark_s002,
)


def test_dataset_s002_reproducible():
    a = generar_datos_s002(n_por_orden=100, seed=7)
    b = generar_datos_s002(n_por_orden=100, seed=7)
    assert np.array_equal(a.counts_ab, b.counts_ab)
    assert np.array_equal(a.counts_ba, b.counts_ba)


def test_modelos_producen_distribuciones_validas():
    modelos = [
        baseline_clasico_estatico(),
        modelo_clasico_secuencial(),
        modelo_vectorial_unitario(),
        modelo_quantum_like(),
    ]
    for ab, ba in modelos:
        assert np.isclose(ab.sum(), 1.0)
        assert np.isclose(ba.sum(), 1.0)
        assert np.all(ab >= 0)
        assert np.all(ba >= 0)


def test_control_vectorial_tiene_efecto_de_orden_observable():
    ab, ba = modelo_vectorial_unitario()
    assert not np.allclose(ab, ba)
    assert np.sum(np.abs(ab - ba)) > 0.9


def test_quantum_like_reduce_el_extremo_del_modelo_puro():
    _, ba_puro = modelo_vectorial_unitario()
    _, ba_mixto = modelo_quantum_like(ruido=0.05)
    assert ba_mixto[0] < ba_puro[0]
    assert ba_mixto[1] > ba_puro[1]


def test_benchmark_devuelve_metricas_para_los_cuatro_modelos():
    resultados = benchmark_s002(
        generar_datos_s002(n_por_orden=100, seed=11)
    )
    assert set(resultados) == {
        "clasico_estatico",
        "clasico_secuencial",
        "vectorial_unitario",
        "quantum_like",
    }
    for metricas in resultados.values():
        assert all(np.isfinite(v) for v in metricas.values())


def test_split_train_test_conserva_los_conteos():
    data = generar_datos_s002(n_por_orden=500, seed=17)
    from saussure_quantum.s002_benchmark import dividir_train_test

    train, test = dividir_train_test(data, proporcion_train=0.8, seed=19)
    assert np.array_equal(train.counts_ab + test.counts_ab, data.counts_ab)
    assert np.array_equal(train.counts_ba + test.counts_ba, data.counts_ba)
    assert train.n_ab > 0 and test.n_ab > 0
    assert train.n_ba > 0 and test.n_ba > 0


def test_modelos_ajustados_generan_predicciones_validas():
    from saussure_quantum.s002_benchmark import (
        ajustar_modelos_s002,
        dividir_train_test,
    )

    data = generar_datos_s002(n_por_orden=300, seed=23)
    train, _ = dividir_train_test(data, seed=29)
    pred = ajustar_modelos_s002(train)
    assert set(pred) == {
        "clasico_estatico",
        "clasico_secuencial",
        "vectorial_unitario",
        "quantum_like",
    }
    for ab, ba in pred.values():
        assert np.isclose(ab.sum(), 1.0, atol=1e-8)
        assert np.isclose(ba.sum(), 1.0, atol=1e-8)
        assert np.all(ab >= 0)
        assert np.all(ba >= 0)


def test_benchmark_ajustado_separa_train_y_test():
    from saussure_quantum.s002_benchmark import benchmark_ajustado_s002

    resultados = benchmark_ajustado_s002(
        generar_datos_s002(n_por_orden=300, seed=31),
        proporcion_train=0.75,
        seed_split=37,
    )
    assert set(resultados) == {
        "clasico_estatico",
        "clasico_secuencial",
        "vectorial_unitario",
        "quantum_like",
    }
    for metricas in resultados.values():
        assert all(np.isfinite(v) for v in metricas.values())
        assert "log_likelihood_train" in metricas
        assert "AIC_train" in metricas
        assert "BIC_train" in metricas
