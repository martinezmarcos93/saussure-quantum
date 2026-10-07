"""Reproducción inicial de QQ sobre las tablas publicadas por Wang/Busemeyer.

Estos tests trabajan con proporciones publicadas, no con microdatos.
No modifican S003 ni convierten las proporciones en conteos artificiales.
"""
import numpy as np

from saussure_quantum.s003_qq import efecto_orden, residuo_qq, validar_conjuntas


DATOS = {
    "clinton_gore": (
        np.array([[0.4899, 0.0447], [0.1767, 0.2886]]),
        np.array([[0.5625, 0.0255], [0.1991, 0.2130]]),
        -0.0030,
    ),
    "white_black": (
        np.array([[0.3987, 0.0174], [0.1612, 0.4227]]),
        np.array([[0.4012, 0.1379], [0.0597, 0.4012]]),
        -0.0190,
    ),
    "rose_jackson": (
        np.array([[0.3379, 0.3241], [0.0178, 0.3202]]),
        np.array([[0.4156, 0.1234], [0.0671, 0.3939]]),
        0.1514,
    ),
}


def test_tablas_publicadas_normalizan():
    for p_ab, p_ba, _ in DATOS.values():
        validar_conjuntas(p_ab, p_ba)
        assert np.isclose(p_ab.sum(), 1.0)
        assert np.isclose(p_ba.sum(), 1.0)


def test_qq_clinton_gore_es_cercano_a_cero():
    p_ab, p_ba, q_esperado = DATOS["clinton_gore"]
    assert np.isclose(residuo_qq(p_ab, p_ba), q_esperado, atol=1e-4)


def test_qq_white_black_es_cercano_a_cero():
    p_ab, p_ba, q_esperado = DATOS["white_black"]
    assert np.isclose(residuo_qq(p_ab, p_ba), q_esperado, atol=1e-4)


def test_qq_rose_jackson_conserva_la_violacion_publicada():
    p_ab, p_ba, q_esperado = DATOS["rose_jackson"]
    assert np.isclose(residuo_qq(p_ab, p_ba), q_esperado, atol=1e-4)
    assert abs(residuo_qq(p_ab, p_ba)) > 0.1


def test_los_tres_casos_muestran_efecto_de_orden():
    for p_ab, p_ba, _ in DATOS.values():
        efecto = efecto_orden(p_ab, p_ba)
        assert efecto["L1"] > 0.0
