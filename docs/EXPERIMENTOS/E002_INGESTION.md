# E002 — Barrida de ingestión y análisis

## Objetivo

Convertir el dataset público de Free Association Database en observaciones canónicas de Saussure-Quantum sin modificar los datos científicos durante la ingestión.

## Fuente

El artículo identifica como fuente de datos el proyecto OSF XZCBG y recomienda para análisis la carpeta de datos limpios. Esos archivos contienen una fila por respuesta, variables demográficas repetidas y la variable Association number para conservar la posición de la respuesta.

## Adaptador

El adapter saussure_quantum/e002_ingest.py:

1. recibe un CSV local;
2. calcula SHA-256 antes de procesarlo;
3. resuelve las columnas obligatorias mediante nombres explícitos o aliases;
4. convierte cada fila en Asociacion;
5. conserva idioma y país cuando están disponibles;
6. registra filas leídas, emitidas y descartadas;
7. rechaza posiciones no enteras en lugar de corregirlas silenciosamente.

No descarga archivos automáticamente. Esto mantiene separadas adquisición y análisis y permite reproducir exactamente qué archivo se utilizó.

## Columnas canónicas

- participante → PS_ID / identificador equivalente;
- estímulo → palabra estímulo;
- respuesta → asociación;
- posición → Association number;
- idioma → Language;
- país → Country of residence, opcional.

La resolución por aliases es deliberadamente conservadora: si falta una variable obligatoria, la ingestión falla.

## Análisis descriptivo

saussure_quantum/e002_analisis.py incorpora:

- resumen por idioma × estímulo;
- número de participantes;
- número total de respuestas;
- número de respuestas únicas;
- entropía de Shannon;
- distribución de respuestas siguientes condicionada por la respuesta anterior.

Esta capa todavía no compara modelos clásicos contra quantum-like.

## Barrida de validación

### B1 — Integridad de fuente
Pendiente: descargar desde OSF el archivo limpio elegido y registrar SHA-256.

### B2 — Compatibilidad de esquema
Pendiente: ejecutar el adapter contra el archivo real y verificar los nombres de columnas.

### B3 — Conteos globales
Pendiente: comprobar que la ingestión reproduce los totales publicados, incluyendo 1.439 participantes y 223.786 respuestas.

### B4 — Conteos por idioma
Pendiente: comprobar los totales publicados por idioma:
- English: 241 / 33.415;
- Estonian: 123 / 17.946;
- French: 316 / 51.441;
- German: 357 / 61.528;
- Italian: 56 / 9.190;
- Lithuanian: 179 / 24.008;
- Spanish: 167 / 26.258.

### B5 — Cobertura por estímulo
Pendiente: verificar que los 62 estímulos aparecen y detectar cobertura desigual o valores faltantes.

### B6 — Posición
Pendiente: verificar distribución de Association number y comprobar que no se destruye la información R1/R2/R3.

### B7 — Reproducibilidad
Pendiente: generar manifest con archivo, SHA-256, fecha, filas antes/después, versión del adapter y filtros.

### B8 — Primer informe descriptivo
Pendiente: producir tablas por idioma/estímulo, diversidad y transición posicional.

## Estado de la barrida

El código y los tests unitarios del adapter están preparados. El entorno actual no dispone de salida de red para descargar OSF y por ello B1–B8 no deben marcarse como ejecutados.

El siguiente paso que requiere al usuario es disponer del archivo limpio localmente y ejecutar la batería. No se deben fabricar resultados para cubrir ese hueco.