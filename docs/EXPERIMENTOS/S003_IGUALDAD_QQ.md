# S003 — Respuestas conjuntas e igualdad QQ

Diseño formal. Los resultados están en [`docs/RESULTADOS_S003.md`](../RESULTADOS_S003.md).

S003 es un benchmark **sintético**. No usa datos humanos y nada de lo que sigue es una afirmación psicológica.

## Por qué existe S003

S002 observaba una sola respuesta binaria en dos órdenes: dos números. Con eso el modelo clásico secuencial era saturado y el quantum-like no podía fallar. S003 registra las **dos** respuestas de cada orden, lo que da seis números observables y una restricción que el modelo proyectivo predice sin parámetros libres.

## Pregunta experimental

Cuando se registran las respuestas conjuntas a dos preguntas dicotómicas en ambos órdenes, ¿cumplen los datos la igualdad QQ? Y si la cumplen, ¿eso distingue un modelo proyectivo quantum-like de un modelo clásico?

## Variables y espacio de resultados

- Dos preguntas, A y B, con respuestas "sí" (índice 0) y "no" (índice 1).
- Dos grupos independientes: uno responde A y después B; el otro, B y después A.
- Por cada orden se observan cuatro resultados conjuntos:

| Orden A→B | Orden B→A |
|---|---|
| p(AyBy), p(AyBn), p(AnBy), p(AnBn) | p(ByAy), p(ByAn), p(BnAy), p(BnAn) |

En el código, `p_ab[i, j]` es la probabilidad de responder `i` a la primera pregunta (A) y `j` a la segunda (B); `p_ba[i, j]`, lo mismo con B primero. Cada orden tiene 3 probabilidades libres: **6 observables** en total.

## Igualdad QQ

Fuente: Wang y Busemeyer (2013), ecuación "QQ Equality" y prueba en el Apéndice.

    p(AyBn) + p(AnBy) = p(ByAn) + p(BnAy)

La probabilidad de dar respuestas distintas a las dos preguntas es la misma en ambos órdenes. Con d_AB = p(AyBn) + p(AnBy) y d_BA = p(ByAn) + p(BnAy), el residuo es

    q = d_AB − d_BA,      y la igualdad afirma q = 0.

Forma equivalente: p(AyBy) + p(AnBn) = p(ByAy) + p(BnAn).

### Supuestos de la derivación

Son los cuatro postulados del modelo QQ de la fuente:

1. **Estado común.** El estado de creencia inicial es el mismo en ambos órdenes (un vector unitario; la derivación vale también para un estado mixto).
2. **Respuestas como subespacios.** Cada respuesta corresponde a un proyector ortogonal; los de una pregunta son mutuamente excluyentes y suman la identidad.
3. **Regla de Born.** P(respuesta) = ‖P·ψ‖².
4. **Regla de Lüders y nada más.** Tras responder, el estado es la proyección normalizada. La fuente lo enuncia como supuesto crítico: lo único que cambia el contexto de una pregunta es haber respondido la anterior.

Bajo esos supuestos la igualdad vale para cualquier dimensión, cualquier rango de los proyectores y cualquier estado. No tiene parámetros.

Derivación directa. Sean P_A y P_B los proyectores del "sí", P̄ = I − P y ⟨·⟩ = Tr(ρ ·). La probabilidad de dar la misma respuesta en el orden A→B es

    p(AyBy) + p(AnBn) = ⟨P_A P_B P_A⟩ + ⟨P̄_A P̄_B P̄_A⟩.

Desarrollando con P² = P:

    P̄_A P̄_B P̄_A = (I − P_A) − (I − P_A) P_B (I − P_A)
                  = I − P_A − P_B + P_A P_B + P_B P_A − P_A P_B P_A,

de modo que

    p(AyBy) + p(AnBn) = 1 − ⟨P_A⟩ − ⟨P_B⟩ + ⟨P_A P_B + P_B P_A⟩.

El lado derecho es simétrico ante el intercambio A ↔ B, así que coincide con p(ByAy) + p(BnAn): la probabilidad de acuerdo, y por tanto la de desacuerdo, es igual en ambos órdenes. ∎

El módulo no implementa esta fórmula: calcula las ocho probabilidades con productos de proyectores y la igualdad emerge. Se verifica numéricamente sobre 3 000 modelos aleatorios (dimensión 2 a 7, rangos varios, estados puros y mixtos) con |q| ≤ 4.4e-16. La prueba original, por otro camino (la ley de reciprocidad), está en el Apéndice de la fuente.

### Qué supuestos son necesarios

Verificado en `tests/test_s003_qq.py::test_supuestos_de_qq_cuales_son_necesarios`:

| Violación | ¿Se conserva QQ? |
|---|---|
| Proyectores "borrosos" E = (1−ε)P + ε(I−P) con instrumento √E | Sí, exactamente, incluso con ε distinto por pregunta |
| Ruido de respuesta igual en ambos órdenes | Sí: q′ = (1−2ε₁)(1−2ε₂)·q |
| POVM genérico (efecto que no es función de un proyector) | No (\|q\| hasta 0.06 en la exploración) |
| Dinámica unitaria entre las dos preguntas | No (mediana de \|q\| ≈ 0.23) |
| Estado inicial distinto en cada orden | No (mediana de \|q\| ≈ 0.07) |
| Ruido de respuesta distinto según el orden | No |

Lebedev y Khrennikov (2018) analizan el caso POVM.

## Modelos

### Proyectivo quantum-like

`probabilidades_proyectivas(rho, P_A, P_B)`: p_AB[i, j] = Tr(P_B^j P_A^i ρ P_A^i P_B^j). El grado de no conmutatividad se controla con θ en `modelo_qubit` (‖[P_A, P_B]‖ = |sin θ|/√2) y con `no_conmutatividad` en `modelo_proyectivo_aleatorio`.

- **Qubit, rango 1**: cumple además la ley de reciprocidad, P(misma respuesta | primera) = cos²(θ/2) en ambos órdenes. Familia de dimensión 3.
- **General** (dimensión ≥ 4, rango 2): familia de dimensión 5, la misma que el plano QQ, pero **no lo llena**: además de QQ debe cumplir las desigualdades de `cotas_proyectivas`.

### Clásicos

| Modelo | Descripción | Dimensión | ¿Cumple QQ? |
|---|---|---:|---|
| Sin orden | una distribución conjunta sobre (A, B); bayesiano conmutativo | 3 | Sí, trivialmente |
| Repetición simétrica | la segunda respuesta copia la primera con probabilidad κ | 3 | **Sí, con efecto de orden** |
| Repetición asimétrica | κ distinta en cada orden | 4 | No: q = (κ_BA − κ_AB)·[a(1−b) + (1−a)b] |
| Markov con estado latente | distribución inicial, emisiones y transiciones dependientes de la respuesta | **6** | No en general |
| Saturado | dos distribuciones conjuntas arbitrarias | 6 | No en general |

El modelo de Markov es el adversario: con sólo dos estados latentes ya es saturado.

### Familia de referencia: plano QQ

`ajustar_qq_saturado`: todas las distribuciones con q = 0 (dimensión 5). No es ni clásica ni cuántica; es la clase que la igualdad caracteriza.

## Hipótesis

- **H0 (clásica).** Un modelo clásico de Markov suficientemente general reproduce las probabilidades conjuntas observadas.
- **H1 (quantum-like).** Los datos provienen de un modelo proyectivo, que impone q = 0 y las cotas de Cauchy–Schwarz.

**H0 no es refutable con este diseño**: el Markov clásico es saturado. Lo que el diseño puede refutar es H1. Por eso la pregunta útil no es "¿clásico o cuántico?" sino "¿sobrevive la predicción proyectiva?" y "¿aporta parsimonia frente al modelo saturado?".

## Predicciones

- **Proyectivo:** q = 0 exactamente, para todo estado y todo par de proyectores, y holgura ≥ 0 en `cotas_proyectivas`.
- **Clásico general:** ninguna restricción. q toma cualquier valor en [−1, 1].
- **Clásicos restringidos:** algunos predicen q = 0 (sin orden, repetición simétrica).

## Posibles violaciones y cómo se leen

| Observación | Lectura |
|---|---|
| q ≠ 0 con potencia suficiente | Refuta el modelo proyectivo con estos supuestos. No dice cuál supuesto falla. |
| q ≈ 0 (equivalencia) y cotas cumplidas | Compatible con el modelo proyectivo **y** con modelos clásicos. No discrimina. |
| q ≈ 0 pero cotas violadas | Refuta el modelo proyectivo aunque pase QQ. |
| q ≈ 0 sin efecto de orden | QQ se cumple trivialmente; no informa. |

## Métricas

- Residuo q, error estándar, intervalo de confianza (Wald y Newcombe), tamaño de efecto (h de Cohen).
- Test z de Wang y Busemeyer y razón de verosimilitud (1 gl) para H: q = 0.
- Test de equivalencia (TOST) para sostener |q| < margen.
- Contraste de efecto de orden (razón de verosimilitud, 3 gl).
- Contraste bootstrap de las cotas proyectivas.
- Comparación de modelos: log-verosimilitud, AIC, BIC, log-verosimilitud fuera de muestra, L1, Jensen–Shannon, calibración (χ² de Pearson en test), recuperación del modelo generador.

## Criterios

**De éxito del experimento** (metodológico): el test tiene el nivel nominal bajo q = 0, potencia conocida bajo q ≠ 0, y las equivalencias observacionales entre modelos están identificadas.

**De falsación del modelo proyectivo**: (a) se rechaza q = 0 con el tamaño muestral fijado por el análisis de potencia, o (b) el intervalo de la holgura de las cotas queda por debajo de 0.

**Lo que no cuenta como evidencia a favor**: no rechazar q = 0. Con poca muestra una violación real pasa el test.

## Tamaño muestral y potencia

La varianza de q̂ es [d_AB(1−d_AB) + d_BA(1−d_BA)]/n. `n_requerido_qq` da el n por orden para una potencia dada y `potencia_qq` la potencia para un n dado; ambas se contrastan con Monte Carlo en los resultados. La regla δ·√n ≳ 3 de S002 se usa sólo como orden de magnitud.

## Problemas de identificabilidad (anticipados y verificados)

1. Clásico de Markov ⊇ todo: reproduce exactamente cualquier distribución proyectiva.
2. Los parámetros del modelo proyectivo (fase del estado, pureza, dimensión, rango) no son recuperables.
3. Existen modelos clásicos restringidos con los mismos observables que modelos proyectivos.

## Limitaciones

- Dos preguntas dicotómicas y dos órdenes. No hay preguntas repetidas ni tres o más preguntas.
- Las cotas de `cotas_proyectivas` son condiciones necesarias demostradas; su suficiencia es un resultado numérico, no un teorema.
- Todos los datos son sintéticos y generados por los modelos que se comparan.
- No se modelan covariables, heterogeneidad entre respondientes ni dependencia entre observaciones.
