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

El siguiente paso es construir el benchmark sintético S002 y su protocolo de comparación de modelos.


## Benchmark computacional S002

El módulo `saussure_quantum/s002_benchmark.py` formaliza cuatro referencias:

| Modelo | Supuesto | Complejidad |
|---|---|---:|
| Clásico estático | una distribución para ambos órdenes | 1 parámetro |
| Clásico secuencial | dos canales estocásticos que pueden no conmutar | 5 parámetros |
| Vectorial unitario | estado + transformaciones unitarias | 2 parámetros en el control |
| Quantum-like | dinámica unitaria + ruido/decoherencia efectiva | 3 parámetros en el control |

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
