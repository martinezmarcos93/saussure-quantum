from pathlib import Path

import pytest

from saussure_quantum.e002_ingest import (
    MapeoColumnasE002,
    ingerir_csv,
    resolver_mapeo,
    sha256_archivo,
)


CSV = """PS_ID,Stimulus,Association,Association number,Language,Country of residence
1,amor,Vida,1,es,AR
1,amor,vínculo,2,es,AR
2,amor,Vida,1,es,ES
"""


def test_resolver_mapeo_con_nombres_publicables():
    mapeo = resolver_mapeo(
        ["PS_ID", "Stimulus", "Association", "Association number", "Language"]
    )
    assert mapeo.participante == "PS_ID"
    assert mapeo.posicion == "Association number"


def test_ingestion_emite_observaciones_y_proveniencia(tmp_path: Path):
    archivo = tmp_path / "sample.csv"
    archivo.write_text(CSV, encoding="utf-8")

    observaciones, metadata = ingerir_csv(archivo)

    assert len(observaciones) == 3
    assert metadata.filas_leidas == 3
    assert metadata.filas_emitidas == 3
    assert metadata.filas_descartadas == 0
    assert len(metadata.sha256) == 64
    assert observaciones[0].participante_id == "1"
    assert observaciones[0].posicion == 1
    assert observaciones[1].pais == "AR"


def test_hash_es_determinista(tmp_path: Path):
    archivo = tmp_path / "sample.csv"
    archivo.write_text("a,b\n1,2\n", encoding="utf-8")
    assert sha256_archivo(archivo) == sha256_archivo(archivo)


def test_ingestion_falla_si_falta_columna_obligatoria(tmp_path: Path):
    archivo = tmp_path / "sample.csv"
    archivo.write_text(
        "PS_ID,Stimulus,Association,Language\n1,amor,Vida,es\n",
        encoding="utf-8",
    )

    with pytest.raises(KeyError):
        ingerir_csv(archivo)


def test_ingestion_rechaza_posicion_no_entera(tmp_path: Path):
    archivo = tmp_path / "sample.csv"
    archivo.write_text(
        "PS_ID,Stimulus,Association,Association number,Language\n"
        "1,amor,Vida,primera,es\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Association number inválido"):
        ingerir_csv(archivo)
