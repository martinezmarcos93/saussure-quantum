# Metodología experimental

## Regla de oro

Primero se define el fenómeno. Después el modelo clásico. Luego el modelo quantum-like. Finalmente se compara capacidad explicativa/predictiva.

## Estructura de un experimento

1. Pregunta.
2. Hipótesis.
3. Variables observables.
4. Dataset.
5. Baseline clásico.
6. Modelo quantum-like.
7. Parámetros.
8. Procedimiento.
9. Predicciones previas.
10. Métricas.
11. Resultado.
12. Análisis de sensibilidad.
13. Limitaciones.
14. Conclusión.

## Controles

Los experimentos deben controlar, cuando corresponda:
- tamaño muestral;
- azar de inicialización;
- sobreajuste;
- leakage;
- selección de parámetros;
- multiplicidad de pruebas;
- sensibilidad al contexto;
- calidad del embedding/dataset.

## Comparación de modelos

Preferir criterios cuantitativos como:
- log-likelihood;
- AIC/BIC;
- RMSE/MAE;
- validación cruzada;
- calibración;
- capacidad predictiva fuera de muestra.

## Reproducibilidad

Cada experimento deberá poder ejecutarse con:
- datos versionados;
- semilla controlada;
- configuración explícita;
- salida estructurada;
- figura/tablas;
- metadatos de versión.

## Criterio de falsación

Si el modelo clásico explica los datos igual o mejor con menor complejidad, el modelo quantum-like no obtiene ventaja en ese experimento.

Esto es un resultado válido y debe conservarse.
