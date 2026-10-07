# Informe final de S003 — respuestas conjuntas e igualdad QQ

Fecha: 2026-10-07. Rama: `research/programa-cuantico-2026`.

Informe de cierre de la fase sintética. El detalle numérico completo está en [`RESULTADOS_S003.md`](RESULTADOS_S003.md) y el diseño formal en [`EXPERIMENTOS/S003_IGUALDAD_QQ.md`](EXPERIMENTOS/S003_IGUALDAD_QQ.md).

Todos los datos son sintéticos. Ningún resultado de este documento es evidencia empírica ni admite lectura psicológica.

## Estado

S003 quedó implementado, validado y cerrado en su fase sintética: la igualdad QQ es una predicción falsable del modelo proyectivo, pero no discrimina modelos clásicos de quantum-like.

## Conclusión científica

- **El generador proyectivo cumple QQ exactamente.** La igualdad sale de los proyectores, no de una fórmula: |q| ≤ 4.4e-16 en 3 000 modelos aleatorios de dimensión 2 a 7, puros y mixtos.
- **Un modelo clásico también la cumple.** El modelo de repetición (la segunda respuesta copia la primera con probabilidad κ) cumple QQ exactamente y tiene efecto de orden, siempre que κ sea igual en ambos órdenes.
- **El Markov clásico es saturado.** Con dos estados latentes reproduce cualquier distribución proyectiva (error < 1e-9), así que H0 no es refutable con este diseño; lo único refutable es H1.
- **Cumplir QQ no es evidencia de estructura cuántica; violarla sí refuta el modelo proyectivo.**
- **Hallazgo nuevo.** El modelo proyectivo no llena el plano QQ: debe cumplir además unas desigualdades de Cauchy–Schwarz, y ocupa cerca del 30 % de ese plano. Existen distribuciones clásicas que pasan QQ y que ningún modelo proyectivo puede generar.
- **La única ventaja del modelo proyectivo es la parsimonia**, y es pequeña: con datos proyectivos, el qubit supera al saturado fuera de muestra por 0.37 unidades de log-verosimilitud.

## Resultados

### Potencia

5 000 réplicas por celda; n por orden.

| \|q\| | n=250 | 1 000 | 5 000 | n para potencia 0.80 | para 0.95 |
|---:|---:|---:|---:|---:|---:|
| 0.02 | 0.07 | 0.15 | 0.54 | 8 880 | 14 700 |
| 0.05 | 0.22 | 0.65 | 1.00 | 1 448 | 2 396 |
| 0.10 | 0.64 | 1.00 | 1.00 | 371 | 613 |

La potencia analítica coincide con la empírica. La regla δ·√n ≳ 3 queda como aproximación gruesa: aquí la potencia 0.80 corresponde a |q|·√n ≈ 1.9.

### Falsos positivos

El test rechaza QQ entre el 4.3 % y el 5.6 % de las veces cuando se cumple, tanto en regímenes proyectivos como clásicos. Los intervalos del 95 % cubren entre 0.943 y 0.958.

### Falsos negativos

Una violación real de 0.105 pasa el test el 66 % de las veces con n = 100, el 33 % con 250 y el 0.4 % con 1 000. Por eso existe un test de equivalencia: para sostener |q| < 0.05 hacen falta unas 2 500 observaciones por orden.

### Ruido

El ruido de respuesta igual en ambos órdenes nunca crea una violación, pero oculta las que existen (con 30 % de ruido, 0.105 es casi indetectable). El ruido que depende del orden rompe QQ en un modelo proyectivo exacto: un rechazo no dice qué supuesto falló.

### Matriz de recuperación

BIC, 100 réplicas, n = 1 000 por orden; familia correcta entre corchetes.

| Generador | sin orden | repetición | qubit | plano QQ | saturado |
|---|---:|---:|---:|---:|---:|
| sin orden | [91] | 9 | 0 | 0 | 0 |
| repetición simétrica | 0 | [100] | 0 | 0 | 0 |
| repetición asimétrica | 0 | 0 | 0 | 0 | [100] |
| Markov genérico | 28 | 0 | 1 | 2 | [69] |
| qubit proyectivo | 0 | 0 | [100] | 0 | 0 |
| proyectivo dim. 4 | 0 | 69 | 0 | [31] | 0 |

- A diferencia de S002, la recuperación mejora con los datos: con 5 000 por orden llega al 99–100 % en los siete regímenes.
- Con pocos datos se confunden clases: con n = 250, los datos proyectivos de dimensión 4 se atribuyen al modelo clásico de repetición el 84 % de las veces.
- La selección por una única partición de test se estanca cerca del 55–60 %, igual que en S002.

## Identificabilidad

- **Clase clásica frente a clase proyectiva: no identificable.** El 57 % de los modelos clásicos de repetición tiene un gemelo proyectivo con observables idénticos.
- **Parámetros proyectivos no recuperables:** fase del estado, pureza, dimensión y rango.
- **Lo que sí se distingue:** los modelos restringidos entre sí (qubit, repetición, sin orden, saturado).
- **Qué observación los separaría:** ninguna, si el adversario es un modelo clásico con estado latente sin restricciones. Solo se puede separar contra modelos clásicos restringidos declarados de antemano.

## Tests antes y después

| Repositorio | Antes | Después |
|---|---|---|
| saussure-quantum | 163 | 296 (163 sin modificar + 133 de S003) |
| laboratorio-cuantico | 174 | 174 (solo documentación) |

Ambas suites pasan completas. No se modificó código ni tests de S001 ni de S002. El benchmark del módulo (`python -m saussure_quantum.s003_qq`) reproduce la matriz con conteos idénticos.

## Archivos modificados

**saussure-quantum** (commits `4ebb54b` a `d6d2ef9`):

- Nuevos:
  - `saussure_quantum/s003_qq.py`
  - `tests/test_s003_qq.py`
  - `docs/EXPERIMENTOS/S003_IGUALDAD_QQ.md`
  - `docs/RESULTADOS_S003.md`
  - `docs/REFERENCIAS.md`
- Actualizados: `Readme.md` y, en `docs/`, `PROGRAMA_INVESTIGACION.md`, `METODOLOGIA.md`, `RESULTADOS_VALIDACION_LOCAL.md` y `EXPERIMENTOS/S002_EFECTO_ORDEN.md`.

**laboratorio-cuantico** (commit `cad1d0b`): en `docs/`, `HIPOTESIS.md`, `EXPERIMENTOS.md`, `METODOLOGIA.md`, `REFERENCIAS.md`, `PROGRAMA_INVESTIGACION.md` y `RESULTADOS_VALIDACION_LOCAL.md`.

## Conclusiones corregidas por ser demasiado fuertes

- El informe de validación local decía que el diseño QQ separaría el modelo quantum-like del clásico de Markov. Solo lo separa del Markov genérico. Quedó corregido en ambos documentos de resultados, conservando el texto original como registro.
- H7 quedó reformulada en `HIPOTESIS.md` (laboratorio-cuantico): superar en ajuste a un baseline clásico general es imposible por construcción en este diseño.
- En el programa de investigación se reemplazó el S003 previsto ("interferencia semántica") por este, y los experimentos posteriores quedaron sin numerar y condicionados a un análisis de identificabilidad previo.

## Limitaciones

- Todo es sintético; no hay evidencia empírica ni lectura psicológica.
- Que las cotas de Cauchy–Schwarz delimiten exactamente lo alcanzable es un resultado numérico (30 puntos), no un teorema.
- De la bibliografía solo se consultó en texto completo Wang y Busemeyer (2013). El resto son resúmenes o citas de memoria, y una de ellas (Kellen, Singmann y Batchelder) no pudo verificarse; está marcada así en [`REFERENCIAS.md`](REFERENCIAS.md).
- La matriz de recuperación usa 100 réplicas por celda (error estándar de hasta 0.05).

## Siguiente experimento recomendado

No se recomienda avanzar a un S004 de modelado más rico. El paso con más valor es contrastar las dos predicciones a priori (QQ y las cotas) contra conjuntos públicos de efectos de orden en encuestas, con el tamaño muestral fijado por el análisis de potencia. Sería el primer resultado empírico del programa, y puede salir negativo.

La alternativa, si se prefiere seguir en sintético, es fijar de antemano un conjunto cerrado de modelos clásicos restringidos y diseñar el experimento que más los separe del proyectivo, incluyendo preguntas repetidas (A–B–A).

La integración con Jung queda fuera por ahora: ningún experimento mostró todavía una señal quantum-like identificable.

## Fuentes

- [Wang y Busemeyer (2013), texto completo](https://jbusemey.pages.iu.edu/quantum/QuestOrdEff.pdf)
- [Boyer-Kassem, Duchêne y Guerci (2016)](https://arxiv.org/abs/1501.04901)
- [Lebedev y Khrennikov (2018)](https://arxiv.org/abs/1811.00045)
