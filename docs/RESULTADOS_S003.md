# Resultados de S003 — respuestas conjuntas e igualdad QQ

Diseño: [`docs/EXPERIMENTOS/S003_IGUALDAD_QQ.md`](EXPERIMENTOS/S003_IGUALDAD_QQ.md). Código: `saussure_quantum/s003_qq.py`. Tests: `tests/test_s003_qq.py`.

Todos los datos son sintéticos. Ningún resultado de este documento es evidencia empírica ni admite lectura psicológica.

## Conclusión

**La igualdad QQ es una predicción falsable del modelo proyectivo, y el test que la contrasta funciona. Pero no discrimina modelos clásicos de modelos quantum-like.**

1. El generador proyectivo cumple QQ exactamente; la igualdad emerge de los proyectores, no de una fórmula.
2. Un modelo clásico de repetición la cumple también, exactamente y con efecto de orden.
3. Un modelo clásico de Markov con dos estados latentes reproduce cualquier distribución proyectiva: es saturado.
4. Por tanto, cumplir QQ no es evidencia de estructura cuántica. Violarla sí refuta el modelo proyectivo.
5. El diseño es mejor que S002: los modelos restringidos se distinguen entre sí y se recuperan con suficientes datos. Lo que no se puede separar es la *clase* clásica de la *clase* proyectiva.
6. La única ventaja del modelo proyectivo es de parsimonia: predice a priori una restricción (QQ y unas cotas adicionales) y ahorra grados de libertad. Esa ventaja es real pero pequeña, y la comparte cualquier modelo restringido que resulte correcto.

## Estado de cada afirmación

| Afirmación | Etiqueta |
|---|---|
| Todo modelo proyectivo cumple q = 0 (cualquier dimensión, rango y estado) | VALIDADO MATEMÁTICAMENTE (derivación) y COMPUTACIONALMENTE (3 000 modelos, \|q\| ≤ 4.4e-16) |
| El modelo proyectivo cumple además las cotas de Cauchy–Schwarz | VALIDADO MATEMÁTICAMENTE (condición necesaria) |
| Esas cotas delimitan exactamente lo alcanzable dentro del plano QQ | VALIDADO COMPUTACIONALMENTE (30 de 30 puntos); no demostrado |
| La repetición simétrica es clásica, cumple QQ y tiene efecto de orden | VALIDADO MATEMÁTICAMENTE |
| El Markov clásico de dos estados es saturado y reproduce las distribuciones proyectivas | VALIDADO COMPUTACIONALMENTE (rango 6; error de ajuste < 1e-9) |
| El test z de QQ tiene nivel 0.05 y la potencia analítica | VALIDADO COMPUTACIONALMENTE |
| Clase clásica frente a clase proyectiva | NO IDENTIFICABLE con este diseño |
| Fase, pureza, dimensión y rango del modelo proyectivo | NO IDENTIFICABLE |
| "QQ distingue cognición cuántica de clásica" | RESULTADO NEGATIVO |
| "QQ es un test falsable del modelo proyectivo" | RESULTADO POSITIVO (metodológico) |
| Que datos humanos cumplan o no QQ | NO TESTEADO; sin EVIDENCIA EMPÍRICA en este repositorio |

## Las diez preguntas de cierre

**1. ¿Qué predice exactamente QQ?** Que la probabilidad de dar respuestas distintas a dos preguntas es la misma en los dos órdenes: p(AyBn) + p(AnBy) = p(ByAn) + p(BnAy). Una ecuación sobre seis observables, sin parámetros.

**2. ¿Bajo qué supuestos?** Mismo estado inicial en ambos órdenes, respuestas como proyectores ortogonales, regla de Born y actualización de Lüders sin otra dinámica entre preguntas. Se conserva con proyectores "borrosos" y con ruido de respuesta igual en ambos órdenes. Se rompe con POVM genéricos, con una evolución unitaria entre preguntas, con estados iniciales distintos por orden y con ruido distinto según el orden.

**3. ¿El generador quantum-like cumple la igualdad?** Sí, exactamente.

**4. ¿Los modelos clásicos también pueden cumplirla?** Sí. El modelo sin orden (trivialmente), el de repetición simétrica (con efecto de orden) y cualquier Markov ajustado a datos que la cumplan.

**5. ¿Qué modelos clásicos pueden violarla?** El de repetición asimétrica, con q = (κ_BA − κ_AB)·[a(1−b) + (1−a)b], y el Markov genérico. El régimen de referencia `markov_generico` tiene q = 0.105.

**6. ¿Cuántos datos necesitamos?** Depende del residuo que se quiera detectar; ver la tabla de potencia. Para q = 0.05, unas 1 450 observaciones por orden (potencia 0.80) o 2 400 (0.95). Para q = 0.02, 8 900 y 14 700.

**7. ¿Qué tamaño de efecto podemos detectar?** Con 1 000 por orden, q ≈ 0.06 con potencia 0.80. Con 10 000, q ≈ 0.02.

**8. ¿Qué observables son necesarios para distinguir modelos?** Las respuestas conjuntas permiten distinguir entre sí los modelos restringidos (qubit, repetición, sin orden, saturado). Ningún conjunto finito de observables de este tipo separa "proyectivo" de "clásico con estado latente", porque el segundo es saturado.

**9. ¿Existe una ventaja predictiva real?** Sólo la de la parsimonia. Con datos proyectivos, el modelo restringido a QQ predice fuera de muestra igual que el saturado (−483.13 frente a −483.14) y el qubit lo supera por 0.37 unidades de log-verosimilitud (−368.64 frente a −369.01), el margen esperable por ahorrar tres parámetros.

**10. ¿O QQ caracteriza una clase de distribuciones que también genera un modelo clásico?** Esto. QQ define un hiperplano de dimensión 5 en un espacio de 6. Los modelos proyectivos ocupan cerca del 30 % de ese hiperplano; el resto sólo es alcanzable clásicamente. Y todo lo que alcanza un modelo proyectivo lo alcanza también uno clásico.

## Estructura de las familias

Dimensión de la familia de distribuciones observables (rango del jacobiano), sobre 6 observables:

| Familia | Dimensión | Cumple QQ |
|---|---:|---|
| Sin orden (clásico) | 3 | sí |
| Repetición simétrica (clásico) | 3 | sí |
| Repetición asimétrica (clásico) | 4 | no |
| Markov, 2 o 3 estados latentes (clásico) | 6 | no |
| Proyectivo, dimensión 2, rango 1 | 3 | sí |
| Proyectivo, dimensión 3, rangos 1 y 2; dimensión 4, rango 1 | 4 | sí |
| Proyectivo, dimensión 4 rango 2; dimensión 5 rango 2; dimensión 6 rango 3 | 5 | sí |
| Plano QQ completo | 5 | sí |

### El modelo proyectivo no llena el plano QQ

Al ajustar modelos proyectivos de dimensión 4 y 6 a puntos arbitrarios del plano QQ, 17 de 30 resultaron inalcanzables (error de ajuste entre 0.003 y 0.20, idéntico en ambas dimensiones). Los 17 violan las cotas de `cotas_proyectivas`; los 13 alcanzables las cumplen. Sin excepciones.

Las cotas: para cada par de respuestas (i a A, j a B), x_ij = Re⟨ψ|P_A^i P_B^j|ψ⟩ se obtiene de los observables y debe cumplir

    x_ij² ≤ p(B_j)·p_AB[i, j]      y      x_ij² ≤ p(A_i)·p_BA[j, i].

Fracción compatible con algún modelo proyectivo:

| Conjunto | Fracción compatible |
|---|---:|
| Plano QQ (muestreo uniforme en su parametrización) | 0.302 ± 0.002 |
| Repetición simétrica, (a, b, κ) uniformes | 0.574 |
| Repetición simétrica con κ = 0.1 / 0.4 / 0.8 | 0.88 / 0.65 / 0.34 |
| Sin orden | 1.000 |

El modelo proyectivo hace, por tanto, **dos** predicciones contrastables: la igualdad QQ y las cotas. Un régimen clásico (`repeticion_incompatible`) pasa la primera y falla la segunda.

## El test de QQ

5 000 réplicas por celda, α = 0.05. Tasa de rechazo de H: q = 0.

| Régimen | q | n=100 | 250 | 500 | 1 000 | 2 500 | 5 000 | 10 000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sin_orden | 0 | 0.051 | 0.048 | 0.048 | 0.050 | 0.052 | 0.052 | 0.054 |
| repeticion_simetrica | 0 | 0.050 | 0.056 | 0.049 | 0.050 | 0.046 | 0.049 | 0.048 |
| repeticion_incompatible | 0 | 0.053 | 0.054 | 0.049 | 0.049 | 0.050 | 0.051 | 0.049 |
| qubit_proyectivo | 0 | 0.049 | 0.052 | 0.049 | 0.053 | 0.049 | 0.051 | 0.048 |
| proyectivo_dim4 | 0 | 0.048 | 0.046 | 0.049 | 0.051 | 0.043 | 0.046 | 0.045 |
| markov_generico | 0.105 | 0.337 | 0.673 | 0.917 | 0.996 | 1.000 | 1.000 | 1.000 |
| repeticion_asimetrica | −0.168 | 0.716 | 0.985 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

- **Falsos positivos** (rechazar QQ cuando se cumple): entre 0.043 y 0.056, el nivel nominal, tanto para los regímenes proyectivos como para los clásicos que cumplen QQ. El test no distingue unos de otros, como debe ser.
- **Falsos negativos** (no rechazar una violación real de 0.105): 66 % con n = 100, 33 % con 250, 8 % con 500, 0.4 % con 1 000.
- **Potencia analítica frente a empírica**: coinciden (0.318 / 0.337, 0.653 / 0.673, 0.915 / 0.917, 0.997 / 0.996 para `markov_generico`).
- **Cobertura de los intervalos del 95 %**: Wald 0.943–0.957, Newcombe 0.944–0.958 en todos los regímenes y tamaños.
- **Estimador**: insesgado; su desvío empírico coincide con el error estándar teórico en la tercera cifra.
- **Distribución del estadístico z bajo q = 0** (20 000 réplicas): cuantiles 2.5 % y 97.5 % de −1.93 / 1.99 (n = 100), −1.98 / 1.96 (n = 1 000), −1.95 / 1.98 (n = 10 000); P(p < 0.01) = 0.010–0.011. El test de Kolmogorov–Smirnov rechaza la normalidad exacta con n ≤ 1 000 porque el estadístico es discreto; las colas, que son lo que usa el test, están bien calibradas.
- **Probabilidades extremas** (desacuerdo 0.02): con n = 100 el test es conservador (0.039) y el intervalo de Newcombe sobrecubre (0.984); desde n = 1 000 ambos son nominales.

### No rechazar no es demostrar

Tasa con que el test de equivalencia declara |q| < 0.05:

| Régimen | n=500 | 1 000 | 2 500 | 5 000 |
|---|---:|---:|---:|---:|
| Regímenes con q = 0 | 0.00–0.51 | 0.48–0.91 | 0.96–1.00 | 1.00 |
| markov_generico (q = 0.105) | 0.000 | 0.000 | 0.000 | 0.000 |

Para *sostener* que los datos cumplen QQ dentro de ±0.05 hacen falta unas 2 500 observaciones por orden. Con n = 100, el 66 % de las muestras de un proceso que viola QQ pasaría el test z sin que eso signifique nada.

## Potencia y tamaño muestral

Tasa de rechazo según el residuo poblacional (5 000 réplicas por celda) y n por orden necesario según la fórmula analítica:

| \|q\| | n=100 | 250 | 500 | 1 000 | 2 500 | 5 000 | 10 000 | n para 0.80 | n para 0.95 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.010 | 0.050 | 0.054 | 0.063 | 0.073 | 0.121 | 0.181 | 0.318 | 35 275 | 58 401 |
| 0.020 | 0.061 | 0.072 | 0.105 | 0.153 | 0.325 | 0.538 | 0.843 | 8 880 | 14 700 |
| 0.030 | 0.075 | 0.110 | 0.169 | 0.288 | 0.612 | 0.886 | 0.994 | 3 973 | 6 576 |
| 0.050 | 0.117 | 0.222 | 0.380 | 0.649 | 0.959 | 0.999 | 1.000 | 1 448 | 2 396 |
| 0.075 | 0.201 | 0.405 | 0.695 | 0.939 | 1.000 | 1.000 | 1.000 | 652 | 1 079 |
| 0.100 | 0.316 | 0.635 | 0.900 | 0.997 | 1.000 | 1.000 | 1.000 | 371 | 613 |
| 0.150 | 0.593 | 0.927 | 0.999 | 1.000 | 1.000 | 1.000 | 1.000 | 168 | 277 |
| 0.200 | 0.822 | 0.995 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 96 | 157 |

La regla δ·√n ≳ 3 de S002 queda como aproximación gruesa: aquí la potencia 0.80 corresponde a |q|·√n entre 1.9 y 2.0, porque depende de la probabilidad de desacuerdo. Debe usarse `n_requerido_qq` con los valores esperados, no la regla.

### Sensibilidad al ruido de respuesta

Ruido igual en ambas posiciones y órdenes, sobre `markov_generico`. El residuo se contrae como (1 − 2ε)².

| ε | q | n=100 | 250 | 500 | 1 000 | 2 500 | 5 000 | 10 000 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.105 | 0.322 | 0.674 | 0.919 | 0.998 | 1.000 | 1.000 | 1.000 |
| 0.10 | 0.067 | 0.163 | 0.336 | 0.586 | 0.852 | 0.998 | 1.000 | 1.000 |
| 0.20 | 0.038 | 0.096 | 0.143 | 0.232 | 0.398 | 0.764 | 0.967 | 1.000 |
| 0.30 | 0.017 | 0.069 | 0.071 | 0.093 | 0.121 | 0.213 | 0.403 | 0.661 |
| 0.40 | 0.004 | 0.058 | 0.050 | 0.059 | 0.059 | 0.061 | 0.076 | 0.098 |

El ruido nunca crea una violación, pero **oculta** las que existen: con un 30 % de respuestas invertidas, una violación de 0.105 es casi indetectable incluso con 10 000 observaciones.

El ruido que depende del orden hace lo contrario: sobre un modelo proyectivo exacto, un ruido del 5 % en la segunda respuesta de un orden y del 15 % en la del otro produce q = −0.045 y el modelo proyectivo se rechaza el 58 % de las veces con n = 1 000. Un rechazo de QQ no dice cuál de los supuestos falló.

## Comparación de modelos

n = 1 000 por orden, 100 réplicas, partición 80/20. Medias. k = dimensión de la familia.

**Generador proyectivo de dimensión 4**

| Modelo | k | LL train | AIC | BIC | LL test | L1 | JS | \|q\| del ajuste | Calibración rechazada |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sin_orden | 3 | −1975.77 | 3957.54 | 3973.68 | −492.33 | 0.204 | 0.0082 | 0 | 0.91 |
| repeticion_simetrica | 3 | −1941.65 | 3889.30 | **3905.44** | −484.17 | 0.105 | 0.0029 | 0 | 0.27 |
| qubit_proyectivo | 3 | −1988.65 | 3983.30 | 3999.44 | −496.37 | 0.225 | 0.0109 | 0 | 0.99 |
| qq_saturado | 5 | −1935.10 | **3880.20** | 3907.09 | **−483.13** | 0.098 | 0.0023 | 0 | 0.10 |
| saturado | 6 | −1934.60 | 3881.21 | 3913.48 | −483.14 | 0.097 | 0.0023 | 0.002 | 0.09 |

**Generador qubit proyectivo**

| Modelo | k | LL train | BIC | LL test | L1 | \|q\| del ajuste | Calibración rechazada |
|---|---:|---:|---:|---:|---:|---:|---:|
| sin_orden | 3 | −1625.93 | 3274.00 | −406.22 | 0.284 | 0 | 1.00 |
| repeticion_simetrica | 3 | −1620.49 | 3263.12 | −404.85 | 0.271 | 0 | 1.00 |
| qubit_proyectivo | 3 | −1474.72 | **2971.57** | **−368.64** | 0.087 | 0 | 0.11 |
| qq_saturado | 5 | −1473.75 | 2984.40 | −368.94 | 0.089 | 0 | 0.16 |
| saturado | 6 | −1473.25 | 2990.77 | −369.01 | 0.089 | 0.0003 | 0.16 |

**Generador clásico de repetición simétrica**

| Modelo | k | LL train | BIC | LL test | L1 | \|q\| del ajuste | Calibración rechazada |
|---|---:|---:|---:|---:|---:|---:|---:|
| repeticion_simetrica | 3 | −1992.56 | **4007.26** | **−495.68** | 0.098 | 0 | 0.05 |
| qubit_proyectivo | 3 | −2028.78 | 4079.70 | −505.58 | 0.199 | 0 | 0.95 |
| qq_saturado | 5 | −1991.52 | 4019.93 | −496.03 | 0.101 | 0 | 0.11 |
| saturado | 6 | −1991.04 | 4026.34 | −496.16 | 0.103 | 0.002 | 0.11 |

**Generador Markov genérico (q = 0.105)**

| Modelo | k | LL train | BIC | LL test | L1 | \|q\| del ajuste | Calibración rechazada |
|---|---:|---:|---:|---:|---:|---:|---:|
| sin_orden | 3 | −2195.07 | 4412.27 | −549.29 | 0.143 | 0 | 0.47 |
| qubit_proyectivo | 3 | −2202.73 | 4427.60 | −551.08 | 0.159 | 0 | 0.65 |
| qq_saturado | 5 | −2189.46 | 4415.81 | −548.48 | 0.138 | 0 | 0.41 |
| saturado | 6 | −2180.20 | **4404.66** | **−546.26** | 0.106 | 0.104 | 0.09 |

"Calibración rechazada" es la fracción de réplicas en que el χ² de Pearson de los datos de test rechaza la predicción (p < 0.05); con 400 observaciones de test y parámetros estimados en train, un modelo correcto queda en torno a 0.05–0.15.

### "Reproduce QQ" no es "explica mejor"

Las cuatro familias restringidas tienen residuo 0 en su ajuste por construcción. Aun así:

- con datos clásicos de repetición, el qubit proyectivo reproduce QQ y explica mal los datos (LL de test −505.6 frente a −495.7; calibración rechazada el 95 % de las veces);
- con datos proyectivos de dimensión 4, el modelo clásico de repetición obtiene el mejor BIC medio a n = 1 000 (3905.4 frente a 3907.1 del plano QQ) aunque no sea el generador;
- el modelo saturado nunca reproduce QQ exactamente y predice igual de bien que el restringido cuando QQ es cierta.

## Matriz de recuperación

100 réplicas por celda. Filas: generador. Columnas: familia seleccionada. La familia correcta (la más pequeña que contiene al generador) va en negrita.

**Por BIC, n = 1 000 por orden**

| Generador | sin orden | repetición | qubit | plano QQ | saturado | Rechazo de QQ |
|---|---:|---:|---:|---:|---:|---:|
| sin_orden | **91** | 9 | 0 | 0 | 0 | 0.06 |
| repeticion_simetrica | 0 | **100** | 0 | 0 | 0 | 0.03 |
| repeticion_incompatible | 0 | **100** | 0 | 0 | 0 | 0.05 |
| repeticion_asimetrica | 0 | 0 | 0 | 0 | **100** | 1.00 |
| markov_generico | 28 | 0 | 1 | 2 | **69** | 0.99 |
| qubit_proyectivo | 0 | 0 | **100** | 0 | 0 | 0.05 |
| proyectivo_dim4 | 0 | 69 | 0 | **31** | 0 | 0.06 |

**Recuperación por BIC según el tamaño muestral**

| Generador | n=250 | 1 000 | 5 000 |
|---|---:|---:|---:|
| sin_orden | 0.80 | 0.91 | 1.00 |
| repeticion_simetrica | 0.94 | 1.00 | 1.00 |
| repeticion_incompatible | 1.00 | 1.00 | 1.00 |
| repeticion_asimetrica | 0.41 | 1.00 | 1.00 |
| markov_generico | 0.06 | 0.69 | 1.00 |
| qubit_proyectivo | 1.00 | 1.00 | 1.00 |
| proyectivo_dim4 | 0.11 | 0.31 | 0.99 |

**Recuperación por log-verosimilitud de test (partición única 80/20)**

| Generador | n=250 | 1 000 | 5 000 |
|---|---:|---:|---:|
| sin_orden | 0.34 | 0.42 | 0.57 |
| repeticion_simetrica | 0.36 | 0.59 | 0.58 |
| qubit_proyectivo | 0.43 | 0.59 | 0.55 |
| proyectivo_dim4 | 0.17 | 0.51 | 0.60 |
| markov_generico | 0.41 | 0.77 | 0.98 |
| repeticion_asimetrica | 0.60 | 0.94 | 1.00 |

Lectura:

- **A diferencia de S002, la recuperación mejora con los datos**: con 5 000 por orden, el BIC recupera la familia correcta en el 99–100 % de los casos en los siete regímenes. No hay empates de BIC en ninguna réplica.
- **Con pocos datos el procedimiento confunde clases.** Con n = 250, datos proyectivos de dimensión 4 se atribuyen al modelo *clásico* de repetición el 84 % de las veces (69 % con n = 1 000); datos de un Markov que viola QQ se atribuyen al modelo sin orden el 61 %.
- **La selección por una única partición de test se estanca cerca del 55–60 %** cuando el generador está en una familia anidada dentro de otras, igual que en S002. No debe usarse como criterio único.
- **Recuperar `plano QQ` no es recuperar un modelo cuántico.** La familia correcta para el generador proyectivo de dimensión 4 es el conjunto de distribuciones que cumplen QQ, que es tan clásico como proyectivo.
- **Recuperar `qubit` tampoco.** Su familia observable (primera respuesta de su marginal; misma respuesta con probabilidad c en ambos órdenes) tiene una descripción clásica inmediata, y el Markov de dos estados la reproduce con error < 1e-9.

## Contraste de las cotas proyectivas

Bootstrap paramétrico (300 remuestras), 100 réplicas por celda. Tasa con que se rechaza la existencia de un modelo proyectivo.

| Régimen | Holgura | q | n=250 | 1 000 | 5 000 | 10 000 |
|---|---:|---:|---:|---:|---:|---:|
| Proyectivos y clásicos compatibles (5 regímenes) | +0.007 a +0.030 | 0 | 0.00–0.01 | 0.00 | 0.00 | — |
| Repetición (0.8, 0.25, κ = 0.45) | −0.004 | 0 | 0.09 | 0.39 | 0.95 | 1.00 |
| Repetición (0.8, 0.25, κ = 0.55) | −0.012 | 0 | 0.49 | 0.98 | 1.00 | 1.00 |
| Repetición (0.8, 0.25, κ = 0.62) | −0.019 | 0 | 0.80 | 1.00 | 1.00 | 1.00 |
| `repeticion_incompatible` (κ = 0.80) | −0.042 | 0 | 1.00 | 1.00 | 1.00 | 1.00 |

El contraste es conservador (falsos rechazos ≤ 1 %) y detecta distribuciones que pasan QQ pero que ningún modelo proyectivo puede generar. Sólo se aplica cuando QQ no se rechaza: los regímenes que violan QQ ya quedan refutados por el test anterior.

## Identificabilidad

Pares explícitos de modelos distintos con los mismos observables (diferencia ≤ 2e-16, en `tests/test_s003_qq.py`):

| Modelo 1 | Modelo 2 | Qué no puede recuperarse |
|---|---|---|
| Qubit con azimut +φ | Qubit con azimut −φ | La fase relativa del estado |
| Qubit con vector de Bloch (0.3, 0, 0.5) | Qubit con (0.3, 0.6, 0.5) | La pureza y la componente fuera del plano de medición |
| Qubit, dimensión 2, rango 1 | El mismo modelo embebido en dimensión 4, rango 2 | La dimensión del espacio y el rango de los proyectores |
| Repetición clásica con a = b = ½ y copia κ | Qubit máximamente mixto con cos²(θ/2) = (1+κ)/2 | Si el mecanismo es clásico o proyectivo |
| Sin orden con respuestas perfectamente correlacionadas | Qubit con θ = 0 | Ídem |
| Cualquier modelo proyectivo | Markov clásico de 2 estados ajustado | Ídem, en general |

El 57 % de los modelos clásicos de repetición simétrica tiene un gemelo proyectivo con observables idénticos.

**Qué observación nueva los separaría.** Ninguna, si el adversario es un modelo clásico con estado latente sin restricciones: con suficientes estados reproduce la distribución de cualquier secuencia finita de respuestas. La separación sólo es posible contra modelos clásicos *restringidos* y declarados de antemano. Por eso el valor de un diseño no está en "probar lo cuántico" sino en someter una predicción a priori, sin parámetros, al riesgo de fallar.

## Validación cruzada del diseño

| Conclusión | ¿Podría producirlo un modelo clásico? | ¿Había potencia? | ¿Es identificable? |
|---|---|---|---|
| El generador proyectivo cumple QQ | Sí (repetición simétrica, Markov ajustado) | Sí: nivel 0.05 exacto | La igualdad sí; la clase de modelo no |
| El régimen Markov genérico viola QQ | Es clásico | Sí desde n ≈ 500 (potencia 0.92) | Sí |
| Las cotas separan `repeticion_incompatible` de lo proyectivo | Es clásico, y eso es lo que se detecta | Sí desde n = 250 | Sí, si la holgura es < −0.01 |
| El qubit se recupera el 100 % de las veces | Su familia tiene descripción clásica | Sí | La familia sí; el mecanismo no |
| Datos proyectivos atribuidos a repetición clásica con n ≤ 1 000 | — | No: hace falta n ≈ 5 000 | Sí, con más datos |

## Limitaciones

- Datos sintéticos generados por los modelos que se comparan. Nada aquí dice cómo responden las personas.
- Siete regímenes de referencia con parámetros fijos; la recuperación depende de qué tan separados están.
- La suficiencia de las cotas de Cauchy–Schwarz es un resultado numérico (30 puntos, dimensiones 4 y 6, estados puros), no un teorema.
- El modelo proyectivo general no se ajusta en la comparación rutinaria; se usa el plano QQ como aproximación, que lo contiene. Cerca de la frontera de las cotas ambas familias difieren.
- La matriz de recuperación usa 100 réplicas por celda: error estándar de hasta 0.05 en cada proporción.
- No se modela heterogeneidad entre respondientes. El residuo q es lineal en las probabilidades, así que una mezcla de individuos que cumplen QQ la cumple también, aunque tengan estados y proyectores distintos. No se estudió si las cotas de Cauchy–Schwarz se conservan bajo mezcla.
- No se corrige por multiplicidad cuando se aplican varios contrastes a los mismos datos.

## Siguiente experimento

S003 queda metodológicamente cerrado en su fase sintética. No corresponde avanzar a un "S004" de modelado más rico hasta decidir entre dos caminos:

1. **Contrastar con datos reales la predicción a priori.** Aplicar `contraste_qq`, `contraste_equivalencia_qq` y `contraste_cotas_proyectivas` a conjuntos públicos de efectos de orden en encuestas, con el tamaño muestral fijado por `n_requerido_qq`. Es el primer paso con contenido empírico del programa, y su resultado puede ser negativo. La pregunta no sería "¿es cuántico?" sino "¿sobrevive la predicción proyectiva donde modelos clásicos restringidos declarados de antemano fallan?".
2. **Si se quiere seguir en sintético**: fijar de antemano un conjunto cerrado de modelos clásicos restringidos con motivación independiente (repetición, anclaje y ajuste, memoria de la respuesta) y diseñar el experimento que maximice la separación entre ellos y el modelo proyectivo, incluyendo preguntas repetidas (A–B–A), donde el modelo proyectivo predice que repetir la misma pregunta de inmediato reproduce la respuesta.

En ambos casos conviene sustituir la selección por partición única por validación cruzada repetida o por un contraste de razón de verosimilitud entre familias anidadas.
