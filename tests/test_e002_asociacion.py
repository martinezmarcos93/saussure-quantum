import math

import pytest

from saussure_quantum.e002_asociacion import (
    Asociacion,
    cobertura_por_estimulo,
    diversidad_normalizada,
    diversidad_shannon,
    frecuencias_respuesta,
    normalizar_respuesta,
    red_asociativa,
    transiciones_por_posicion,
    validar_asociaciones,
)


OBS = [
    Asociacion("p1", "amor", "  Vida ", 1, "es"),
    Asociacion("p1", "amor", "vida", 2, "es"),
    Asociacion("p1", "amor", " vínculo ", 3, "es"),
    Asociacion("p2", "amor", "Vida", 1, "es"),
    Asociacion("p2", "amor", "afecto", 2, "es"),
    Asociacion("p2", "paz", "armonía", 1, "es"),
]


def test_normalizacion_conserva_unidades_lexicas():
    assert normalizar_respuesta("  Vida   ") == "vida"


def test_validacion_basica():
    validar_asociaciones(OBS)


def test_frecuencias_agregan_respuestas_normalizadas():
    frecuencias = frecuencias_respuesta(OBS, estimulo_id="amor")
    assert frecuencias["vida"] == 3
    assert frecuencias["vínculo"] == 1
    assert frecuencias["afecto"] == 1


def test_entropia_y_version_normalizada():
    frecuencias = {"a": 2, "b": 2}
    assert math.isclose(diversidad_shannon(frecuencias), math.log(2))
    assert math.isclose(diversidad_normalizada(frecuencias), 1.0)


def test_entropia_vacia():
    assert diversidad_shannon({}) == 0.0
    assert diversidad_normalizada({}) == 0.0


def test_red_asociativa():
    red = red_asociativa(OBS)
    assert red["amor"]["vida"] == 3
    assert red["amor"]["vínculo"] == 1


def test_transiciones_respetan_posicion():
    transiciones = transiciones_por_posicion(OBS)
    assert transiciones[("vida", "vida")] == 1
    assert transiciones[("vida", "vínculo")] == 1
    assert transiciones[("vida", "afecto")] == 1


def test_cobertura_por_estimulo():
    assert cobertura_por_estimulo(OBS) == {"amor": 2, "paz": 1}


def test_invariantes_rechazan_posicion_invalida():
    with pytest.raises(ValueError):
        validar_asociaciones([Asociacion("p1", "x", "y", 0, "es")])
