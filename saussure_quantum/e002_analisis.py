"""Análisis descriptivo de E002, sin supuestos de modelo."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from saussure_quantum.e002_asociacion import (
    Asociacion,
    diversidad_shannon,
    frecuencias_respuesta,
    normalizar_respuesta,
)


@dataclass(frozen=True)
class ResumenGrupo:
    idioma: str
    estimulo: str
    participantes: int
    respuestas: int
    respuestas_unicas: int
    entropia: float


def resumir_por_idioma_estimulo(
    observaciones: Iterable[Asociacion],
) -> list[ResumenGrupo]:
    grupos: dict[tuple[str, str], list[Asociacion]] = defaultdict(list)
    participantes: dict[tuple[str, str], set[str]] = defaultdict(set)

    for obs in observaciones:
        key = (obs.idioma, obs.estimulo_id)
        grupos[key].append(obs)
        participantes[key].add(obs.participante_id)

    resultado = []
    for (idioma, estimulo), grupo in sorted(grupos.items()):
        frecuencias = frecuencias_respuesta(grupo)
        resultado.append(
            ResumenGrupo(
                idioma=idioma,
                estimulo=estimulo,
                participantes=len(participantes[(idioma, estimulo)]),
                respuestas=len(grupo),
                respuestas_unicas=len(frecuencias),
                entropia=diversidad_shannon(frecuencias),
            )
        )
    return resultado


def distribucion_siguiente(
    observaciones: Iterable[Asociacion],
    *,
    idioma: str | None = None,
    estimulo_id: str | None = None,
) -> dict[str, Counter[str]]:
    """Estima conteos R(n+1) condicionados por la respuesta previa."""
    grupos: dict[tuple[str, str], list[Asociacion]] = defaultdict(list)

    for obs in observaciones:
        if idioma is not None and obs.idioma != idioma:
            continue
        if estimulo_id is not None and obs.estimulo_id != estimulo_id:
            continue
        grupos[(obs.participante_id, obs.estimulo_id)].append(obs)

    resultado: dict[str, Counter[str]] = defaultdict(Counter)
    for grupo in grupos.values():
        ordenadas = sorted(grupo, key=lambda x: x.posicion)
        for anterior, siguiente in zip(ordenadas, ordenadas[1:]):
            resultado[normalizar_respuesta(anterior.respuesta)][
                normalizar_respuesta(siguiente.respuesta)
            ] += 1

    return dict(resultado)
