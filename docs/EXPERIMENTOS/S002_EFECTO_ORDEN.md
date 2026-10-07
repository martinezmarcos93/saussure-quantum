# S002 — Efecto de orden semántico

## Pregunta

¿Cambia la interpretación de un signo cuando dos contextos se aplican en órdenes diferentes?

## Modelo

Comparar:

    A → B

contra:

    B → A

Si los operadores contextuales no conmutan:

    AB ≠ BA

entonces el orden puede convertirse en una variable experimental.

## Ejemplo conceptual

Signo: PADRE

Contexto A: autoridad.
Contexto B: abandono.

No se debe asumir que la combinación produce un efecto de orden. Debe medirse.

## Baselines

1. actualización clásica estática;
2. modelo clásico secuencial;
3. modelo vectorial;
4. modelo quantum-like con operadores no conmutativos.

## Métricas

- diferencia L1 entre distribuciones;
- KL/Jensen-Shannon cuando sea apropiado;
- log-likelihood;
- AIC/BIC;
- predicción fuera de muestra.

## Criterio

La mera existencia de AB ≠ BA no demuestra una ventaja quantum-like: un modelo clásico dinámico también puede producir efectos de orden.

La pregunta científica es qué modelo explica mejor los datos con una complejidad razonable.


## Implementación quantum-like inicial

Se incorporó un control con operadores unitarios generados por matrices Hermitianas:

U_A = exp(−i θ_A G_A),  
U_B = exp(−i θ_B G_B).

Cuando [G_A,G_B] ≠ 0, en general U_A U_B ≠ U_B U_A. El experimento compara las distribuciones finales de A→B y B→A y registra simultáneamente la norma de Frobenius del conmutador de los generadores.

Control recomendado para dimensión 2:

- estado inicial: |+⟩ = (|0⟩+|1⟩)/√2;
- G_A = X;
- G_B = Z;
- θ_A = θ_B = π/4.

Este control produce un efecto de orden observable en la distribución medida y sirve para validar la implementación. No constituye todavía evidencia de una ventaja quantum-like sobre datos cognitivos reales.

## Criterio epistemológico

La existencia de AB ≠ BA sólo demuestra que el formalismo implementado es no conmutativo. Para sostener una hipótesis de contextualidad semántica se deberá:

1. definir un dataset observable;
2. ajustar el baseline clásico y el modelo quantum-like;
3. evitar comparar modelos con distinto número de grados de libertad sin penalización;
4. evaluar ajuste y predicción fuera de muestra;
5. reportar incertidumbre y tamaño de efecto;
6. aceptar explícitamente un resultado nulo si el baseline clásico explica los datos igual o mejor.

### Ajuste y evaluación fuera de muestra

`benchmark_ajustado_s002()` divide el dataset en train/test, ajusta cada familia exclusivamente sobre train y calcula las métricas predictivas sobre test.

Los parámetros ajustados son:

- clásico estático: una probabilidad compartida;
- clásico secuencial: estado inicial + dos canales estocásticos binarios, cinco parámetros;
- vectorial unitario: θ_A y θ_B, manteniendo X/Z como generadores del control;
- quantum-like: θ_A, θ_B y ruido efectivo.

El split es reproducible mediante una semilla. El ajuste usa múltiples inicializaciones deterministas para reducir la dependencia de un único punto inicial.

La lectura correcta de los resultados es:

1. `log_likelihood_train`, `AIC_train` y `BIC_train` describen el ajuste penalizado sobre los datos usados para estimar los parámetros.
2. `log_likelihood`, `L1_medio` y `JS_medio` corresponden al conjunto test y son las métricas principales de generalización.
3. Un menor AIC/BIC no reemplaza la evaluación fuera de muestra.
4. Una ventaja quantum-like sólo sería relevante si persiste fuera de muestra frente a los baselines y no desaparece al introducir un modelo clásico suficientemente flexible.

### Limitación de identificabilidad

El dataset S002 sigue siendo deliberadamente pequeño en estructura: sólo observa la distribución final de cada orden. Por ello, el modelo clásico secuencial de cinco parámetros puede estar débilmente identificado con datos agregados. El AIC/BIC penaliza esta complejidad, pero no convierte mágicamente el problema en identificable.

Una futura versión experimental deberá registrar también estados intermedios, por ejemplo después de A y después de B, o utilizar múltiples condiciones/contextos. Eso permitirá estimar mejor las transiciones clásicas y distinguir entre explicaciones dinámicas alternativas.

### Próximo control científico

El siguiente escalón no debe ser "probar que gana quantum-like", sino comprobar recuperación de modelo generador. Se generarán datasets bajo varios regímenes conocidos —sin efecto de orden, clásico secuencial y unitario/quantum-like— y se verificará si el procedimiento de selección recupera correctamente el régimen cuando dispone de información suficiente.



## Benchmark computacional S002

El módulo `saussure_quantum/s002_benchmark.py` formaliza cuatro referencias:

| Modelo | Supuesto | Parámetros declarados | Dimensión de la familia observable |
|---|---|---:|---:|
| Clásico estático | una distribución para ambos órdenes | 1 | 1 |
| Clásico secuencial | dos canales estocásticos que pueden no conmutar | 5 | 2 (modelo saturado) |
| Vectorial unitario | estado + transformaciones unitarias | 2 | 1 |
| Quantum-like | dinámica unitaria + ruido/decoherencia efectiva | 3 | 1 (la misma familia que el vectorial) |

Con resultados binarios y dos órdenes sólo hay dos números observables. La última columna es el rango del jacobiano de la predicción respecto de los parámetros; ver `docs/RESULTADOS_VALIDACION_LOCAL.md`.

El dataset sintético por defecto utiliza:

- AB = (0.50, 0.50)
- BA = (0.95, 0.05)
- 2000 observaciones por orden
- semilla 2026

El régimen está elegido para que el modelo vectorial puro produzca aproximadamente
(0.50, 0.50) para AB y (1.00, 0.00) para BA, mientras que el modelo quantum-like
con ruido 0.05 suaviza el extremo BA hacia (0.975, 0.025). Esto es un control
metodológico, no una afirmación sobre datos psicológicos.

Esto no representa datos humanos: es un banco de pruebas para verificar que las métricas detectan un efecto de orden conocido.

Las métricas implementadas son L1 medio, Jensen-Shannon medio, log-likelihood, AIC y BIC.

### Interpretación

El benchmark no debe concluir "quantum-like" sólo porque el modelo genera AB ≠ BA. El baseline clásico secuencial también puede hacerlo. La implementación actual establece el benchmark de predicción con parámetros controlados. La siguiente capa será el ajuste de parámetros sobre train y la evaluación sobre test; hasta entonces, AIC/BIC se interpretan sólo como métricas de los modelos parametrizados bajo el control elegido, no como selección definitiva de modelo.


## S002.1 — Recuperación del modelo generador

Antes de pasar a datos cognitivos reales, el protocolo debe demostrar que puede distinguir —o detectar correctamente la indistinguibilidad— entre regímenes conocidos.

Se incorporó una batería de cuatro generadores sintéticos:

| Régimen generador | Propiedad esperada |
|---|---|
| `sin_orden` | AB y BA comparten distribución |
| `clasico_secuencial` | existe dinámica contextual clásica no conmutativa |
| `vectorial_unitario` | evolución por operadores unitarios X/Z |
| `quantum_like` | evolución unitaria más ruido efectivo |

La función `generar_datos_regimen_s002()` produce observaciones multinomiales a partir de las probabilidades exactas de cada régimen. `evaluar_recuperacion_s002()` repite el ciclo completo de generación → split → ajuste → evaluación y registra qué familia resulta seleccionada.

Se registran dos criterios independientes:

- máxima log-verosimilitud predictiva sobre test;
- mínimo BIC sobre train.

La métrica de recuperación es la proporción de réplicas en las que el procedimiento selecciona la familia que generó los datos.

### Qué significaría un resultado negativo

Si el régimen generador quantum-like no es recuperado, no se debe manipular el benchmark hasta obtener una recuperación positiva. Las posibilidades incluyen:

1. falta de información en las observaciones finales;
2. equivalencia observacional entre modelos;
3. exceso de flexibilidad del baseline clásico;
4. parametrización inadecuada del modelo quantum-like;
5. tamaño muestral insuficiente.

Esto es precisamente lo que el control pretende revelar.

### Límite actual

Los cuatro regímenes comparten observaciones agregadas únicamente en los estados finales AB y BA. Por ello, esta batería evalúa recuperación bajo información limitada, no identificación estructural completa.

El siguiente salto experimental deberá incorporar observaciones intermedias y múltiples contextos. Sólo entonces podremos preguntar si una dinámica quantum-like explica patrones que un modelo clásico dinámico no puede reproducir sin una complejidad sustancialmente mayor.

## Estado de S002

S002 queda dividido en cuatro capas:

1. control matemático de no conmutatividad;
2. benchmark con parámetros fijados;
3. ajuste train/test;
4. recuperación del modelo generador.

La batería local se ejecutó el 2026-10-06/07. Resultados completos, tablas y condiciones en [`docs/RESULTADOS_VALIDACION_LOCAL.md`](../RESULTADOS_VALIDACION_LOCAL.md).

## Resultado de S002

**S002 queda cerrado con resultado negativo para el diseño, no para la hipótesis.** El benchmark funciona como software, pero el diseño (resultado binario, dos órdenes, control |+⟩ con X y Z) no puede dar soporte a una ventaja quantum-like ni refutarla:

1. El modelo clásico secuencial es saturado: reproduce cualquier par de distribuciones (p_AB, p_BA). Ningún modelo puede ajustar mejor.
2. El modelo vectorial y el quantum-like predicen exactamente la misma familia (p_AB ≡ ½, p_BA libre). El ruido no es identificable. En 1 000 ajustes su log-verosimilitud de test nunca difirió en más de 4.9e-6.
3. En la matriz de recuperación (50 réplicas, n = 1 000 por orden) el régimen quantum-like no se recupera nunca con BIC nominal (0 de 50, en todos los tamaños muestrales y niveles de ruido) y sólo en 8 de 50 por verosimilitud de test, donde el desempate lo decide el ruido del optimizador.
4. Con datos generados fuera de la familia unitaria, el procedimiento selecciona un modelo unitario entre el 34 % y el 64 % de las veces en la zona de potencia intermedia: el diseño produce falsos positivos a favor de la clase quantum-like.
5. Un efecto de orden se detecta de forma fiable sólo cuando δ·√n ≳ 3 (δ = desvío de p_BA respecto de ½, n = observaciones por orden).

Lo que el código hace ahora con esto: informa parámetros efectivos y un BIC efectivo junto a los nominales, detecta empates (`modelos_empatados_s002`) en lugar de forzar un ganador, e informa la recuperación por clase observacional.

## Siguiente experimento (S003, ya ejecutado)

Un diseño en el que el modelo quantum-like pueda fallar: registrar las dos respuestas en cada orden y contrastar la **igualdad QQ** (Wang y Busemeyer, 2013), que un modelo proyectivo predice sin parámetros libres y un modelo clásico de Markov genérico viola. Antes de usar datos reales deberá repetirse la recuperación de modelo sobre ese diseño.

Hecho: ver [`S003_IGUALDAD_QQ.md`](S003_IGUALDAD_QQ.md) y [`docs/RESULTADOS_S003.md`](../RESULTADOS_S003.md). Una corrección a lo dicho arriba: el modelo clásico de Markov *genérico* viola la igualdad QQ, pero S003 muestra que un modelo clásico restringido la cumple y que el Markov general es saturado. La igualdad permite refutar el modelo proyectivo, no separar lo clásico de lo quantum-like.

S002 se conserva sin cambios como benchmark de identificabilidad.
