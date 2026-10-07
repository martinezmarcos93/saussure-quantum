# E001-EMP — QQ sobre datos humanos

**Estado:** diseño reproducible; datos publicados reconstruidos desde la fuente primaria.

## Objetivo

Aplicar S003 sin modificarlo a datos humanos publicados sobre efectos de orden de preguntas.

## Datos iniciales

La fuente primaria publica tres encuestas Gallup con muestras de aproximadamente 1.000 adultos: Clinton–Gore, White–Black y Rose–Jackson. Cada encuesta divide la muestra y aplica los dos órdenes de las mismas preguntas. La tabla publicada contiene las cuatro celdas conjuntas para cada orden. citeturn0search0

Clinton–Gore, A→B:
- Cy/Gy = 0.4899
- Cy/Gn = 0.0447
- Cn/Gy = 0.1767
- Cn/Gn = 0.2886

Gore→Clinton:
- Cy/Gy = 0.5625
- Cy/Gn = 0.0255
- Cn/Gy = 0.1991
- Cn/Gn = 0.2130

White–Black, A→B:
- Wy/By = 0.3987
- Wy/Bn = 0.0174
- Wn/By = 0.1612
- Wn/Bn = 0.4227

Black→White:
- Wy/By = 0.4012
- Wy/Bn = 0.1379
- Wn/By = 0.0597
- Wn/Bn = 0.4012

Rose–Jackson, A→B:
- Ry/Jy = 0.3379
- Ry/Jn = 0.3241
- Rn/Jy = 0.0178
- Rn/Jn = 0.3202

Jackson→Rose:
- Ry/Jy = 0.4156
- Ry/Jn = 0.1234
- Rn/Jy = 0.0671
- Rn/Jn = 0.3939

## Reglas

1. No modificar S003 para acomodar estos datos.
2. Reconstruir cada tabla como distribución conjunta.
3. Verificar normalización.
4. Calcular desacuerdo por orden.
5. Calcular el residuo QQ exactamente como en S003.
6. Ejecutar el contraste QQ y registrar intervalo/incertidumbre.
7. Separar claramente orden effect de QQ equality.
8. Comparar con los baselines clásicos ya declarados en S003.
9. No inferir ontología cuántica a partir de QQ.
10. No tratar como idénticos el valor reconstruido a partir de una tabla redondeada y el estadístico publicado en el artículo.

## Control de redondeo y procedencia

La tabla de Wang y Busemeyer presenta proporciones redondeadas a cuatro decimales, mientras que el artículo reporta los estadísticos QQ con mayor precisión. Por ello, la implementación conserva dos campos conceptualmente distintos:

- **q_reconstruido:** resultado obtenido aplicando la definición de S003 a las cuatro celdas publicadas.
- **q_reportado:** valor QQ publicado por la fuente primaria.

Para Clinton–Gore, las celdas mostradas producen q = -0.0032 por aritmética directa, mientras que la publicación reporta q = -0.0031. Para White–Black, las celdas producen q = -0.0190 y la publicación reporta q = -0.0189. Rose–Jackson coincide en q = 0.1514. La diferencia de las dos primeras parejas es compatible con el redondeo de las proporciones publicadas y no debe interpretarse como una discrepancia del modelo.

La fuente primaria reporta para Clinton–Gore q = -0.0031 y para White–Black q = -0.0189; para Rose–Jackson q = 0.1514. citeturn0search0

## Control de límites

Rose–Jackson debe conservarse como caso de fallo esperado. La fuente primaria informa q = 0.1514 y chi-cuadrado(1) = 28.57, p < 0.001. Los autores explican que en este caso se introdujo información adicional sobre los jugadores y que, por tanto, el estado contextual no fue modificado únicamente por el orden de las preguntas. En consecuencia, el modelo QQ básico no es el modelo adecuado para ese diseño. citeturn0search0turn0search8

Este caso no se descarta. Se conserva como motivación para una extensión futura con contexto o transformación intermedia explícita.

## Interpretación prevista

Un resultado compatible con QQ reproduce una restricción del modelo proyectivo bajo sus supuestos, pero no demuestra que el proceso cognitivo sea físicamente cuántico ni identifica de manera exclusiva el modelo quantum-like.

Un rechazo de QQ indica que al menos una condición del modelo no se sostiene en los datos; no identifica por sí solo cuál condición falla.

## Fuente primaria

Wang, Z. & Busemeyer, J. R. (2013), *A Quantum Question Order Model Supported by Empirical Tests of an A Priori and Precise Prediction*, *Topics in Cognitive Science*. La publicación contiene la tabla de las seis pruebas de efectos de orden y explicita que la QQ equality depende del supuesto de que el único factor que modifica el estado/contexto es la pregunta precedente. citeturn0search0

También se utiliza el estudio de context effects publicado en PNAS/PMC que reproduce la lógica de las tablas y define q como la suma de los efectos de contexto sobre una diagonal. citeturn0search8

## Próximo trabajo

- Mantener el fixture de estos tres datasets.
- Añadir pruebas de normalización y QQ.
- Ejecutar S003 sin modificar su lógica.
- Generar informe de reproducción.
- Pasar después a datos individuales o replicaciones abiertas de question-order.
- En paralelo, preparar la cartografía del Free Association Database como candidato P0-B: 1.439 participantes, 223.786 respuestas, 62 estímulos y siete idiomas, con datos crudos y procesados disponibles en OSF. citeturn0search1
