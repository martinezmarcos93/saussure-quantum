from saussure_quantum.e002_analisis import (
    distribucion_siguiente,
    resumir_por_idioma_estimulo,
)
from saussure_quantum.e002_asociacion import Asociacion


OBS = [
    Asociacion("p1", "amor", "vida", 1, "es"),
    Asociacion("p1", "amor", "vínculo", 2, "es"),
    Asociacion("p1", "amor", "afecto", 3, "es"),
    Asociacion("p2", "amor", "vida", 1, "es"),
    Asociacion("p2", "amor", "amor", 2, "es"),
]


def test_resumen_por_idioma_y_estimulo():
    resumen = resumir_por_idioma_estimulo(OBS)
    assert len(resumen) == 1
    assert resumen[0].idioma == "es"
    assert resumen[0].estimulo == "amor"
    assert resumen[0].participantes == 2
    assert resumen[0].respuestas == 5
    assert resumen[0].respuestas_unicas == 4


def test_distribucion_siguiente_preserva_contexto_posicional():
    siguiente = distribucion_siguiente(OBS)
    assert siguiente["vida"]["vínculo"] == 1
    assert siguiente["vida"]["amor"] == 1
    assert siguiente["vínculo"]["afecto"] == 1
