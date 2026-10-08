# E002 — Asociación libre multilingüe

**Estado:** especificación técnica inicial; sin resultados empíricos todavía.

## 1. Fenómeno

El dataset contiene asociaciones libres ante 62 palabras estímulo. Cada participante ve los 62 estímulos en uno de siete idiomas y recibe la instrucción de escribir las primeras tres palabras que le vienen a la mente; algunos participantes producen menos de tres respuestas y algunas respuestas son frases cortas. El dataset limpio conserva cada respuesta en una fila y una variable de posición de asociación.

El recurso contiene 1.439 participantes y 223.786 respuestas en siete idiomas y 14 países. La muestra española comprende 167 participantes y 26.258 respuestas.

## 2. Pregunta científica

¿La estructura de las asociaciones humanas puede representarse mejor mediante distribuciones y grafos contextuales que mediante una representación puramente frecuencial, y qué regularidades se mantienen o cambian entre individuos, estímulos e idiomas?

La pregunta no presupone una geometría quantum-like.

## 3. Unidad de análisis

La unidad primaria será:

participante × estímulo × posición de asociación

con atributos opcionales: idioma, país de residencia/origen, sesión/fecha cuando estén disponibles y respuesta normalizada.

La posición no se descartará: las respuestas 1, 2 y 3 permiten estudiar si la asociación cambia dentro de la misma tarea.

## 4. Pipeline

OSF raw/cleaned → adapter → observaciones canónicas → controles de calidad → estadísticas descriptivas → red asociativa → dinámica posicional → comparación entre idiomas → modelos clásicos → modelos contextuales.

La publicación recomienda los datasets limpios y normalizados para análisis y proporciona codebooks para las variables.

## 5. Primera batería, sin teoría cuántica

### A. Frecuencia

- frecuencia absoluta y relativa de cada respuesta;
- número de respuestas únicas;
- cobertura por estímulo;
- distribución de longitudes.

### B. Diversidad

- entropía de Shannon;
- entropía normalizada;
- concentración de respuestas;
- diversidad individual frente a agregada.

### C. Estructura de red

Construir un grafo dirigido estímulo → respuesta con peso igual a la frecuencia de asociación.

Posteriormente, respuesta → respuesta para estudiar encadenamientos dentro de las tres posiciones.

### D. Dinámica posicional

Comparar:

P(R1 | estímulo)

con:

P(R2 | estímulo, R1)

y:

P(R3 | estímulo, R1, R2).

Esto permite preguntar si la asociación posterior es independiente de la anterior o si existe una dinámica contextual observable.

### E. Comparación intercultural

Comparar distribuciones por idioma, estímulo, país y grupo de participantes.

No se interpretarán diferencias culturales como diferencias psicológicas esenciales sin controlar composición muestral y cobertura.

## 6. Baselines

El orden de complejidad será deliberadamente creciente:

1. frecuencia marginal;
2. modelo categórico por estímulo;
3. modelo condicionado por idioma;
4. modelo condicionado por estímulo + idioma;
5. modelo secuencial R2|R1 y R3|R1,R2;
6. modelo de grafo;
7. representación vectorial/semántica;
8. sólo si aparece una anomalía que lo justifique, representación contextual quantum-like.

Cada modelo debe evaluarse fuera de muestra cuando la estructura lo permita.

## 7. Métricas

Primarias:

- log-likelihood predictiva;
- cross-entropy;
- Brier score cuando exista una distribución categórica comparable;
- distancia entre distribuciones;
- calibración;
- error de transición para los modelos secuenciales.

La parsimonia se reportará con cautela. AIC/BIC no se usarán como única evidencia cuando existan parámetros no identificables o modelos singulares.

## 8. Hipótesis exploratorias

H1 — Las distribuciones de asociación dependen fuertemente del estímulo.

H2 — El idioma modifica la distribución asociativa incluso después de controlar el estímulo.

H3 — La posición de respuesta contiene información predictiva sobre la siguiente asociación.

H4 — Las estructuras de red presentan regularidades compartidas entre idiomas, pero con variación específica de cada lengua/cultura.

H5 — Si los modelos contextuales aportan capacidad predictiva adicional estable frente a baselines clásicos, se evaluará posteriormente si una representación quantum-like ofrece una descripción parsimoniosa de ese contexto.

H5 no es una predicción del dataset; es un criterio de continuación experimental.

## 9. Jung, Campbell y Psyche Simulacra

No se introducirán arquetipos como etiquetas de entrenamiento.

El procedimiento posterior, si los datos muestran clusters estables, será:

estructura emergente → cluster → descripción semántica → comparación exploratoria con Jung/Campbell.

Una coincidencia con una categoría junguiana no constituye validación de la teoría de Jung.

Los resultados robustos podrán posteriormente transformarse en componentes de representación de estado para Psyche Simulacra/Hanna, pero sólo después de superar la validación empírica.

## 10. Reproducibilidad

Fuente: Free Association Database, OSF, DOI 10.17605/OSF.IO/XZCBG. Los datos están disponibles sin restricciones y bajo CC-BY 4.0 según la publicación.

La ingestión deberá conservar:

- versión/fuente;
- hash del archivo;
- fecha de descarga;
- código de limpieza utilizado;
- filtros aplicados;
- número de filas antes/después;
- reglas de normalización;
- exclusiones;
- semilla cuando exista muestreo.

No se comenzará el modelado empírico hasta poder reconstruir estos metadatos.
