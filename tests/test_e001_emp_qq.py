"""Reproducción inicial de QQ sobre las tablas publicadas por Wang/Busemeyer.

Estos tests trabajan con proporciones publicadas, no con microdatos.
No modifican S003 ni convierten las proporciones en conteos artificiales.
"""

import numpy as np

from saussure_quantum.s003_qq import efecto_orden, residuo_qq, validar_conjuntas


DATOS = {
    "clinton_gore": {
        "p_ab": np.array([[0.4899, 0.0447], [0.1767, 0.2886]]),
        "p_ba": np.array([[0.5625, 0.0255], [0.1991, 0.2130]]),
        # La tabla publicada, al reconstruirse con sus valores redondeados,
        # produce -0.0032. El artículo reporta -0.0031.
        "q_reconstruido": -0.0032,
        "q_reportado": -0.0031,
    },
    "white_black": {
        "p_ab": np.array([[0.3987, 0.0174], [0.1612, 0.4227]]),
        "p_ba": np.array([[0.4012, 0.1379], [0.0597, 0.4012]]),
        "q_reconstruido": -0.0190,
        "q_reportado": -0.0189,
    },
    "rose_jackson": {
        "p_ab": np.array([[0.3379, 0.3241], [0.0178, 0.3202]]),
        "p_ba": np.array([[0.4156, 0.1234], [0.0671, 0.3939]]),
        "q_reconstruido": 0.1514,
        "q_reportado": 0.1514,
    },
}


def test_tablas_publicadas_normalizan():
    for datos in DATOS.values():
        p_ab, p_ba = datos["p_ab"], datos["p_ba"]
        validar_conjuntas(p_ab, p_ba)
        assert np.isclose(p_ab.sum(), 1.0)
        assert np.isclose(p_ba.sum(), 1.0)


def test_qq_reconstruye_clinton_gore_desde_la_tabla_redondeada():
    datos = DATOS["clinton_gore"]
    assert np.isclose(
        residuo_qq(datos["p_ab"], datos["p_ba"]),
        datos["q_reconstruido"],
        atol=1e-4,
    )


def test_qq_reproduce_white_black():
    datos = DATOS["white_black"]
    assert np.isclose(
        residuo_qq(datos["p_ab"], datos["p_ba"]),
        datos["q_reconstruido"],
        atol=1e-4,
    )


def test_qq_rose_jackson_conserva_la_violacion_publicada():
    datos = DATOS["rose_jackson"]
    q = residuo_qq(datos["p_ab"], datos["p_ba"])
    assert np.isclose(q, datos["q_reconstruido"], atol=1e-4)
    assert abs(q) > 0.1


def test_los_tres_casos_muestran_efecto_de_orden():
    for datos in DATOS.values():
        efecto = efecto_orden(datos["p_ab"], datos["p_ba"])
        assert efecto["L1"] > 0.0


def test_valores_reportados_se_conservan_como_metadato():
    assert DATOS["clinton_gore"]["q_reportado"] == -0.0031
    assert DATOS["white_black"]["q_reportado"] == -0.0189
    assert DATOS["rose_jackson"]["q_reportado"] == 0.1514
