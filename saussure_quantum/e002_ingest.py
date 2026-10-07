"""Ingestión reproducible del Free Association Database.

La capa no descarga datos. Recibe un CSV/XLSX ya obtenido del repositorio,
resuelve columnas mediante un mapa explícito o aliases declarados y produce
observaciones canónicas de E002.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from saussure_quantum.e002_asociacion import Asociacion


@dataclass(frozen=True)
class MapeoColumnasE002:
    participante: str
    estimulo: str
    respuesta: str
    posicion: str
    idioma: str
    pais: str | None = None


@dataclass(frozen=True)
class MetadatosIngestion:
    archivo: str
    sha256: str
    filas_leidas: int
    filas_emitidas: int
    filas_descartadas: int


ALIASES = {
    "participante": ("PS_ID", "Participant ID", "participant_id", "Response ID"),
    "estimulo": ("Stimulus", "Stimulus word", "stimulus", "stimulus_id"),
    "respuesta": ("Association", "Response", "association", "response"),
    "posicion": ("Association number", "Association Number", "association_number", "position"),
    "idioma": ("Language", "language", "Survey language", "survey_language"),
    "pais": ("Country of residence", "country_of_residence", "Country"),
}


def sha256_archivo(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolver_columna(
    encabezados: Iterable[str],
    nombre: str,
    aliases: Mapping[str, tuple[str, ...]] = ALIASES,
) -> str:
    encabezados = list(encabezados)
    if nombre in encabezados:
        return nombre

    candidatos = aliases.get(nombre, ())
    for candidato in candidatos:
        if candidato in encabezados:
            return candidato

    raise KeyError(
        f"No se encontró columna '{nombre}'. "
        f"Encabezados disponibles: {encabezados}"
    )


def resolver_mapeo(
    encabezados: Iterable[str],
    *,
    override: Mapping[str, str] | None = None,
) -> MapeoColumnasE002:
    override = dict(override or {})
    campos = {
        campo: resolver_columna(
            encabezados,
            override.get(campo, campo),
        )
        for campo in ("participante", "estimulo", "respuesta", "posicion", "idioma")
    }

    pais = override.get("pais")
    if pais is None:
        try:
            pais = resolver_columna(encabezados, "pais")
        except KeyError:
            pais = None

    return MapeoColumnasE002(**campos, pais=pais)


def ingerir_csv(
    path: str | Path,
    *,
    mapeo: MapeoColumnasE002 | None = None,
    encoding: str = "utf-8-sig",
) -> tuple[list[Asociacion], MetadatosIngestion]:
    path = Path(path)
    sha = sha256_archivo(path)
    observaciones: list[Asociacion] = []
    leidas = 0
    descartadas = 0

    with path.open("r", encoding=encoding, newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("CSV sin encabezados")

        mapeo = mapeo or resolver_mapeo(reader.fieldnames)

        for row in reader:
            leidas += 1
            participante = str(row[mapeo.participante]).strip()
            estimulo = str(row[mapeo.estimulo]).strip()
            respuesta = str(row[mapeo.respuesta]).strip()
            idioma = str(row[mapeo.idioma]).strip()

            if not participante or not estimulo or not respuesta or not idioma:
                descartadas += 1
                continue

            try:
                posicion = int(str(row[mapeo.posicion]).strip())
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Association number inválido en fila {leidas}: "
                    f"{row[mapeo.posicion]!r}"
                ) from exc

            pais = (
                str(row[mapeo.pais]).strip()
                if mapeo.pais is not None and row.get(mapeo.pais) is not None
                else None
            )

            observaciones.append(
                Asociacion(
                    participante_id=participante,
                    estimulo_id=estimulo,
                    respuesta=respuesta,
                    posicion=posicion,
                    idioma=idioma,
                    pais=pais or None,
                )
            )

    metadata = MetadatosIngestion(
        archivo=str(path),
        sha256=sha,
        filas_leidas=leidas,
        filas_emitidas=len(observaciones),
        filas_descartadas=descartadas,
    )
    return observaciones, metadata
