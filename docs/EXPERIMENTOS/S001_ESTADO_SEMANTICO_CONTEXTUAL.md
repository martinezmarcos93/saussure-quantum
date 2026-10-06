# S001 — Estado semántico contextual

## Objetivo

Convertir el concepto de "significado dependiente del contexto" en una variable observable.

## Ejemplo

Signo:

    AGUA

Contextos:

    mar
    bautismo
    nacimiento
    contaminación

El estado inicial contiene varias interpretaciones posibles. Cada contexto modifica la distribución.

## Modelos

### Baseline clásico

Se parte de:

    pᵢ = |αᵢ|²

y se aplica un peso contextual:

    pᵢ' = pᵢ wᵢ / Σⱼ pⱼ wⱼ

### Modelo quantum-like

El contexto actúa sobre las amplitudes:

    αᵢ' = αᵢ √wᵢ

seguido de normalización.

Esta distinción parece pequeña para contextos diagonales. Precisamente por eso S001 es un control: establece la infraestructura antes de introducir operadores no conmutativos.

## Métricas

- distribución posterior;
- entropía;
- fidelidad;
- distancia L1;
- estabilidad ante repetición.

## Hipótesis

H1. El contexto desplaza sistemáticamente la distribución.
H2. Para filtros diagonales simples, el modelo quantum-like no necesariamente superará al baseline clásico.

## Importancia

Un resultado donde ambos modelos sean equivalentes es deseable: demuestra que no estamos usando formalismo cuántico por obligación.

## Siguiente paso

Introducir contextos representados por operadores que no conmutan. Allí aparece el verdadero experimento de orden.
