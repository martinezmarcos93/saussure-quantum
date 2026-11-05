"""
lexicon.py - Léxico real del español para poblar signos-cuanto

Construye, a partir del treebank UD_Spanish-AnCora (CoNLL-U, lema + UPOS
por palabra), un léxico por categoría gramatical con frecuencias. Sirve
de base real para PoetaCuantico en vez de las listas de 6 palabras del
ejemplo original.

Fuente: UniversalDependencies/UD_Spanish-AnCora (CC BY 4.0).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

UPOS_A_CATEGORIA = {
    "NOUN": "sustantivos",
    "ADJ": "adjetivos",
    "ADV": "adverbios",
    "VERB": "verbos",
    "CCONJ": "conectores",
    "SCONJ": "conectores",
}

RUTA_LEXICON_DEFAULT = Path(__file__).parent / "recursos" / "lexicon_es.json"


def _es_lema_valido(lema: str) -> bool:
    return len(lema) >= 2 and lema.isalpha()


def construir_lexicon(
    ruta_conllu: str | Path,
    *,
    min_frecuencia: int = 3,
    max_por_categoria: int = 4000,
) -> Dict[str, List[Tuple[str, int]]]:
    """
    Parsea un archivo CoNLL-U y cuenta frecuencias de lema por categoría.

    Args:
        ruta_conllu: Archivo .conllu (columnas ID, FORM, LEMMA, UPOS, ...)
        min_frecuencia: Descarta lemas con menos ocurrencias que esto
        max_por_categoria: Tope de lemas más frecuentes por categoría

    Returns:
        Diccionario categoria -> lista de (lema, frecuencia) ordenada
        por frecuencia descendente.
    """
    conteos: Dict[str, Counter] = {cat: Counter() for cat in set(UPOS_A_CATEGORIA.values())}

    with Path(ruta_conllu).open("r", encoding="utf-8") as fh:
        for linea in fh:
            if not linea.strip() or linea.startswith("#"):
                continue
            campos = linea.rstrip("\n").split("\t")
            if len(campos) < 4:
                continue
            id_tok = campos[0]
            if "-" in id_tok or "." in id_tok:
                # Tokens multi-palabra (p. ej. contracciones) o nodos vacíos
                continue
            lema, upos = campos[2].strip().lower(), campos[3].strip()
            categoria = UPOS_A_CATEGORIA.get(upos)
            if categoria is None or not _es_lema_valido(lema):
                continue
            conteos[categoria][lema] += 1

    lexicon: Dict[str, List[Tuple[str, int]]] = {}
    for categoria, contador in conteos.items():
        mas_comunes = [
            (lema, freq) for lema, freq in contador.most_common(max_por_categoria)
            if freq >= min_frecuencia
        ]
        lexicon[categoria] = mas_comunes

    return lexicon


def guardar_lexicon(lexicon: Dict[str, List[Tuple[str, int]]], ruta_salida: str | Path) -> None:
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with ruta_salida.open("w", encoding="utf-8") as fh:
        json.dump(lexicon, fh, ensure_ascii=False, indent=0)


def cargar_lexicon(ruta: str | Path = RUTA_LEXICON_DEFAULT) -> Dict[str, List[Tuple[str, int]]]:
    with Path(ruta).open("r", encoding="utf-8") as fh:
        bruto = json.load(fh)
    return {cat: [(lema, freq) for lema, freq in entradas] for cat, entradas in bruto.items()}


if __name__ == "__main__":
    import sys

    ruta_conllu = sys.argv[1] if len(sys.argv) > 1 else "data/es_ancora-ud-train.conllu"
    lex = construir_lexicon(ruta_conllu)
    for cat, entradas in lex.items():
        print(f"{cat}: {len(entradas)} lemas (ej: {[l for l, _ in entradas[:5]]})")
    guardar_lexicon(lex, RUTA_LEXICON_DEFAULT)
    print(f"\nGuardado en {RUTA_LEXICON_DEFAULT}")
