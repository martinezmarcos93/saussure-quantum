# Auditoría matemática S003 — 2026-10-07

## Alcance

Revisión de la implementación y de las afirmaciones matemáticas de S003 en main, con atención a QQ, cotas de Cauchy–Schwarz, dimensionalidad efectiva, Markov, inferencia, potencia, tamaño muestral y comparación de familias.

## Dictamen

S003 es matemáticamente sólido en su resultado central, pero varias afirmaciones deben clasificarse como resultados numéricos y no como teoremas. No corresponde iniciar S004 todavía.

### 1. Igualdad QQ — APROBADA

probabilidades_proyectivas() implementa correctamente la probabilidad secuencial de Lüders: p_AB(i,j) = Tr(P_B^j P_A^i rho P_A^i P_B^j). La batería verifica QQ para estados puros y mixtos, distintas dimensiones y rangos.

Clasificación: teorema + validación computacional.

Referencia: https://onlinelibrary.wiley.com/doi/10.1111/tops.12040

### 2. QQ no identifica una explicación cuántica — APROBADA

modelo_repeticion() proporciona un contraejemplo clásico explícito: q = (kappa_BA - kappa_AB)[a(1-b) + (1-a)b]. Con kappa_AB = kappa_BA, QQ se cumple exactamente y puede existir efecto de orden.

Por tanto, QQ = 0 no implica estructura cuántica; q distinto de 0 refuta el modelo proyectivo bajo sus supuestos; y un modelo clásico restringido puede satisfacer QQ.

### 3. Cotas de Cauchy–Schwarz — APROBADAS COMO NECESARIAS

La construcción de cotas_proyectivas() es correcta como condición necesaria. Para x_ij = Re Tr(rho P_A^i P_B^j), Cauchy–Schwarz produce x_ij² <= p(B_j) p_AB(i,j) y x_ij² <= p(A_i) p_BA(j,i).

La prueba no demuestra suficiencia.

### 4. Suficiencia de las cotas — NO DEMOSTRADA

La evidencia de que las cotas delimitan exactamente la región proyectiva proviene de una exploración de 30 puntos y ajustes en dimensiones 4 y 6. Eso no es una demostración global.

Debe etiquetarse como evidencia numérica compatible con suficiencia, no como teorema.

### 5. Markov de dos estados — REBAJAR LA AFIRMACIÓN

El rango jacobiano 6 demuestra saturación local de la parametrización en los puntos examinados. Los ajustes también reproducen varios regímenes proyectivos.

Pero rango 6 más algunos ajustes exitosos no demuestra que la imagen global sea todo el simplex de seis dimensiones.

La documentación debe decir: modelo Markov de dos estados localmente saturado y capaz de reproducir los regímenes de referencia probados. La afirmación global de saturación queda abierta hasta disponer de una construcción analítica.

### 6. Dimensiones efectivas — APROBADAS COMO RESULTADOS NUMÉRICOS

Los rangos reportados —sin orden 3, repetición simétrica 3, qubit 3, plano QQ 5, saturado 6— son coherentes con el espacio observable de seis dimensiones.

dimension_efectiva() usa diferencias finitas y tolerancia numérica, por lo que estos valores son resultados computacionales reproducibles, no teoremas.

### 7. El 30.2 % del plano QQ — NO ES UNA CONSTANTE UNIVERSAL

El valor aproximado 0.302 depende de la parametrización usada para muestrear el plano QQ. No hay una medida uniforme canónica definida por el código.

Debe describirse como fracción observada bajo el esquema de muestreo empleado. 17/30 frente a 13/30 es una exploración ilustrativa, no una medida geométrica universal.

### 8. Test QQ — APROBADO PARA SU HIPÓTESIS

El test z implementado corresponde al contraste de dos proporciones independientes bajo H0: q = 0. Las simulaciones reportan nivel próximo a 0.05 y la potencia coincide con la aproximación normal en los regímenes estudiados.

Es correcto distinguir no rechazo de equivalencia: el TOST con alpha 0.05 usa un intervalo de 90 %.

### 9. Tamaño muestral — CORREGIDO

Se encontró un caso degenerado en n_requerido_qq(): con d_AB=1 y d_BA=0 la fórmula normal puede devolver n=0 aunque un experimento requiere al menos una observación por orden.

Se corrigió la validación de probabilidades y alpha y se impuso n >= 1. La fórmula continúa siendo una aproximación normal y debe tratarse con cautela en probabilidades extremas.

### 10. Bootstrap de las cotas — PROCEDIMIENTO EMPÍRICO

contraste_cotas_proyectivas() genera el bootstrap desde el MLE restringido a QQ, no desde el conjunto nulo completo de distribuciones proyectivas.

Por ello funciona como contraste/indicador empírico respaldado por simulación, pero no debe presentarse todavía como un test formal de nivel alfa para la hipótesis de existencia de un modelo proyectivo.

Las restricciones y parámetros en frontera pueden producir inferencia no estándar.

### 11. AIC/BIC y parámetros efectivos — PRECAUCIÓN

N_PARAMS_S003 representa dimensión observable efectiva, no necesariamente el número de parámetros regulares identificables de una parametrización.

Esto es relevante porque el qubit y los modelos proyectivos tienen redundancias y parámetros no identificables. BIC no debe tratarse como evidencia decisiva entre familias singulares sin una justificación adicional.

### 12. Resultado científico actual

1. El modelo proyectivo predice QQ.
2. QQ puede cumplirse exactamente en modelos clásicos.
3. Las cotas de Cauchy–Schwarz añaden restricciones proyectivas no triviales.
4. Todavía no está demostrado que esas cotas sean suficientes.
5. Todavía no existe evidencia humana en el repositorio.
6. No hay base para integrar estos resultados con arquetipos jungianos.

## Acciones realizadas en esta rama

- Corregido n_requerido_qq() para casos degenerados.
- Añadido test de regresión para probabilidades extremas y validación de alpha.
- Documentada la separación entre teoremas, resultados numéricos y afirmaciones abiertas.

## Próximo paso

1. Ejecutar la suite completa de saussure-quantum.
2. Verificar el nuevo test.
3. Rebajar en RESULTADOS_S003 cualquier afirmación que presente saturación global de Markov o el 30.2 % como hecho universal.
4. Si todo pasa, fusionar la auditoría.
5. Sólo entonces buscar datos humanos públicos para el primer contraste empírico.

## Referencias

- Wang & Busemeyer (2013), A Quantum Question Order Model Supported by Empirical Tests of an A Priori and Precise Prediction.
- Yearsley & Busemeyer (2016), Quantum Cognition and Decision Theories: A Tutorial.
- Pothos & Busemeyer (2022), Quantum Cognition.