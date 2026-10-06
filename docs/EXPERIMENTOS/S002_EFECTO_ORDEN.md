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
- θ_A = θ_B = π/2.

Este control produce un efecto de orden deliberadamente fuerte y sirve para validar la implementación. No constituye todavía evidencia de una ventaja quantum-like sobre datos cognitivos reales.

## Criterio epistemológico

La existencia de AB ≠ BA sólo demuestra que el formalismo implementado es no conmutativo. Para sostener una hipótesis de contextualidad semántica se deberá:

1. definir un dataset observable;
2. ajustar el baseline clásico y el modelo quantum-like;
3. evitar comparar modelos con distinto número de grados de libertad sin penalización;
4. evaluar ajuste y predicción fuera de muestra;
5. reportar incertidumbre y tamaño de efecto;
6. aceptar explícitamente un resultado nulo si el baseline clásico explica los datos igual o mejor.

El siguiente paso es construir el benchmark sintético S002 y su protocolo de comparación de modelos.
