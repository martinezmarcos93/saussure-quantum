# Referencias

Regla: cada ecuación tomada de la literatura se registra con su fuente y con el lugar del código o de la documentación donde se usa. La literatura sirve para formular hipótesis y restricciones, no para convertir analogías en hechos.

## Efectos de orden e igualdad QQ (S003)

**Wang, Z. y Busemeyer, J. R. (2013).** A quantum question order model supported by empirical tests of an a priori and precise prediction. *Topics in Cognitive Science*, 5(4), 689–710. doi:10.1111/tops.12040

Consultada en texto completo. De aquí se tomó:

| Qué | Dónde está en la fuente | Dónde se usa |
|---|---|---|
| Los cuatro postulados del modelo QQ (estado, respuestas como subespacios, regla de Born, regla de Lüders) | Sección 2 | Supuestos de `docs/EXPERIMENTOS/S003_IGUALDAD_QQ.md` |
| p(AxBy) = ‖P_By P_Ax S‖² | Sección 2 | `probabilidades_proyectivas` |
| Igualdad QQ: p(AyBn) + p(AnBy) = p(ByAn) + p(BnAy) | Ecuación "QQ Equality", sección 4 | `residuo_qq` |
| q = p_AB − p_BA y test z de diferencia de proporciones con varianza 2p(1−p)/N bajo H0 | Ecuación "q-test", sección 4 | `contraste_qq` (campos `z`, `p_valor`) |
| Supuesto crítico: sólo responder la pregunta anterior cambia el contexto | Sección 4 | Supuesto 4 del diseño |
| Ley de reciprocidad para proyecciones de rango 1 | Sección 4 y nota 3 | `modelo_qubit`, `_qubit_desde_parametros` |
| Prueba algebraica de la igualdad | Apéndice | Citada; S003 incluye además una derivación propia más corta |
| "Los modelos de Markov en general no predicen la igualdad QQ" | Sección 6.2 | Punto de partida de la fase adversarial; S003 muestra que el Markov general tampoco la *excluye* y que es saturado |

**Wang, Z., Solloway, T., Shiffrin, R. M. y Busemeyer, J. R. (2014).** Context effects produced by question orders reveal quantum nature of human judgments. *Proceedings of the National Academy of Sciences*, 111(26), 9431–9436.

Contraste de la igualdad QQ sobre un conjunto grande de encuestas. No se tomó ninguna ecuación ni dato; se cita como el principal antecedente empírico. No consultada en texto completo en esta etapa.

**Niestegge, G. (2008).** Derivación independiente de la misma propiedad en un análisis axiomático de la teoría cuántica. Citada a través de Wang y Busemeyer (2013, Apéndice); no consultada directamente.

**Boyer-Kassem, T., Duchêne, S. y Guerci, É. (2016).** Testing quantum-like models of judgment for question order effect. *Mathematical Social Sciences*, 80, 33–46. doi:10.1016/j.mathsocsci.2016.01.001

Consultado el resumen. Deriva las ecuaciones de "Gran Reciprocidad" que deben cumplir los modelos quantum-like *no degenerados* (proyectores de rango 1) e informa que fallan en la mayoría de los conjuntos de datos, lo que obligaría a usar versiones degeneradas. Es coherente con el resultado de S003 de que el modelo de qubit impone restricciones mucho más fuertes que QQ. No se tomó ninguna ecuación.

**Lebedev, A. y Khrennikov, A. (2018).** Quantum-like modeling of the order effect in decision making: POVM viewpoint on the Wang–Busemeyer QQ-equality. arXiv:1811.00045.

Consultado el resumen. Muestra que con observables POVM la igualdad QQ puede violarse. S003 lo reproduce numéricamente (`test_supuestos_de_qq_cuales_son_necesarios`) y precisa que los proyectores "borrosos" con instrumento √E sí la conservan. No se tomó ninguna ecuación.

**Kellen, D., Singmann, H. y Batchelder, W. H. (2018).** Classic-probability accounts of mirrored (quantum-like) order effects in human judgments. *Decision*, 5(4), 323–338.

Referencia citada de memoria, **no verificada ni consultada** en esta etapa: debe confirmarse antes de usarla en cualquier publicación. Se anota porque trata la cuestión que S003 responde por construcción (modelos de probabilidad clásica que satisfacen QQ).

## Inferencia estadística

**Newcombe, R. G. (1998).** Interval estimation for the difference between independent proportions: comparison of eleven methods. *Statistics in Medicine*, 17(8), 873–890.

Intervalo híbrido de puntuación (método 10) para la diferencia de dos proporciones independientes, construido a partir de los intervalos de Wilson de cada proporción. Se usa en `contraste_qq` (campo `ic_newcombe`) y en `contraste_equivalencia_qq`. Fórmula escrita de memoria y validada por su cobertura empírica en `docs/RESULTADOS_S003.md`.

**Schuirmann, D. J. (1987).** A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability. *Journal of Pharmacokinetics and Biopharmaceutics*, 15(6), 657–680.

Procedimiento de dos tests unilaterales (TOST) para equivalencia, aplicado como "intervalo de nivel 1 − 2α dentro del margen" en `contraste_equivalencia_qq`. Citada de memoria.

## Resultados propios de S003 (no tomados de la literatura)

Se derivan y verifican en este repositorio; si alguno coincide con un resultado publicado, la coincidencia no fue consultada:

- el modelo clásico de repetición con κ simétrica cumple QQ con efecto de orden;
- un modelo clásico de Markov con dos estados latentes es saturado para este diseño;
- las desigualdades de `cotas_proyectivas` y el hecho numérico de que delimitan lo alcanzable por un modelo proyectivo dentro del plano QQ.

## Marco general

- Busemeyer, J. R. y Bruza, P. D. (2012). *Quantum Models of Cognition and Decision*. Cambridge University Press.
- Pothos, E. M. y Busemeyer, J. R. (2013). Can quantum probability provide a new direction for cognitive modeling? *Behavioral and Brain Sciences*, 36(3), 255–274.
- Saussure, F. de (1916). *Cours de linguistique générale*.
