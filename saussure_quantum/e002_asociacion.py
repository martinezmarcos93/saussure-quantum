"""Herramientas agnósticas de modelo para el E002 de asociación libre.

El módulo trabaja sobre observaciones ya canonizadas. No incorpora categorías
junguianas, embeddings ni hipótesis quantum-like: esas capas pertenecen a
experimentos posteriores.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Asociacion:
    participante_id: str
    estimulo_id: str
    respuesta: str
    posicion: int
    idioma: str
    pais: str | None = None


def normalizar_respuesta(texto: str) -> str:
    """Normaliza whitespace y casing sin alterar el contenido léxico."""
    return " ".join(texto.strip().casefold().split())


def validar_asociaciones(observaciones: Iterable[Asociacion]) -> None:
    """Valida invariantes mínimos del esquema canónico."""
    for obs in observaciones:
        if not obs.participante_id:
            raise ValueError("participante_id vacío")
        if not obs.estimulo_id:
            raise ValueError("estimulo_id vacío")
        if not obs.respuesta:
            raise ValueError("respuesta vacía")
        if obs.posicion < 1:
            raise ValueError("posicion debe ser >= 1")
        if not obs.idioma:
            raise ValueError("idioma vacío")


def frecuencias_respuesta(observaciones: Iterable[Asociacion], *, estimulo_id: str | None = None, idioma: str | None = None) -> Counter[str]:
    """Cuenta respuestas, opcionalmente filtradas por estímulo e idioma."""
    counter: Counter[str] = Counter()
    for obs in observaciones:
        if estimulo_id is not None and obs.estimulo_id != estimulo_id:
            continue
        if idioma is not None and obs.idioma != idioma:
            continue
        counter[normalizar_respuesta(obs.respuesta)] += 1
    return counter


def diversidad_shannon(frecuencias: Mapping[str, int]) -> float:
    """Entropía de Shannon de una distribución de respuestas."""
    total = sum(frecuencias.values())
    if total <= 0:
        return 0.0
    return -sum((n / total) * log(n / total) for n in frecuencias.values() if n > 0)


def diversidad_normalizada(frecuencias: Mapping[str, int]) -> float:
    """Entropía de Shannon normalizada a [0, 1]."""
    k = len(frecuencias)
    if k <= 1:
        return 0.0
    return diversidad_shannon(frecuencias) / log(k)


def red_asociativa(observaciones: Iterable[Asociacion]) -> dict[str, Counter[str]]:
    """Construye un grafo dirigido estímulo -> respuesta con pesos."""
    red: dict[str, Counter[str]] = defaultdict(Counter)
    for obs in observaciones:
        red[obs.estimulo_id][normalizar_respuesta(obs.respuesta)] += 1
    return dict(red)


def transiciones_por_posicion(observaciones: Iterable[Asociacion]) -> Counter[tuple[str, str]]:
    """Cuenta pares de respuestas consecutivas dentro de participante/estímulo."""
    grupos: dict[tuple[str, str], list[Asociacion]] = defaultdict(list)
    for obs in observaciones:
        grupos[(obs.participante_id, obs.estimulo_id)].append(obs)

    transiciones: Counter[tuple[str, str]] = Counter()
    for grupo in grupos.values():
        ordenadas = sorted(grupo, key=lambda x: x.posicion)
        for anterior, siguiente in zip(ordenadas, ordenadas[1:]):
            transiciones[(normalizar_respuesta(anterior.respuesta), normalizar_respuesta(siguiente.respuesta))] += 1
    return transiciones


def cobertura_por_estimulo(observaciones: Sequence[Asociacion]) -> dict[str, int]:
    """Número de participantes distintos por estímulo."""
    participantes: dict[str, set[str]] = defaultdict(set)
    for obs in observaciones:
        participantes[obs.estimulo_id].add(obs.participante_id)
    return {estimulo: len(ids) for estimulo, ids in participantes.items()}
