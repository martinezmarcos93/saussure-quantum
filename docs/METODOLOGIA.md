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

## Identificabilidad antes que ajuste

Lección de S002 y S003. Antes de comparar modelos sobre un diseño:

1. contar los observables libres del diseño;
2. calcular la dimensión de la familia observable de cada modelo (rango del jacobiano), no sus parámetros declarados;
3. buscar explícitamente pares de modelos distintos con los mismos observables;
4. comprobar que el modelo clásico de control no sea saturado y, si lo es, decirlo: un modelo saturado no puede ser refutado ni superado en ajuste;
5. ejecutar la recuperación del modelo generador y aceptar el resultado.

## Tres preguntas para cada conclusión

- Resultado positivo: ¿podría producirlo también un modelo clásico?
- Resultado negativo: ¿tenía el diseño potencia para detectar el efecto?
- Diferencia entre modelos: ¿es identificable con los observables registrados?

## Inferencia

- Distinguir valor poblacional, estimador, error estándar, intervalo de confianza y tamaño de efecto.
- No rechazar una igualdad no la demuestra. Para sostener que una cantidad es nula se usa un test de equivalencia con un margen fijado de antemano.
- El tamaño muestral se fija con un análisis de potencia antes de recolectar datos.

## Etiquetas de estado

Cada afirmación de un informe lleva una de estas etiquetas: validado matemáticamente, validado computacionalmente, evidencia empírica, no identificable, no testeado, resultado negativo, resultado positivo.

## Criterio de falsación

Si el modelo clásico explica los datos igual o mejor con menor complejidad, el modelo quantum-like no obtiene ventaja en ese experimento.

Esto es un resultado válido y debe conservarse.
