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
