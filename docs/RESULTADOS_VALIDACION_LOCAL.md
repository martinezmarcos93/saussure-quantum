# Resultados de la validación local

Este documento registra una auditoría local completa del repositorio. Distingue en todo momento dos conclusiones diferentes:

- **el software funciona**: el código calcula lo que dice calcular;
- **la hipótesis científica recibe soporte**: los datos favorecen una afirmación sobre el significado.

El resultado principal es negativo y se declara como tal: **con el diseño actual de S002, la hipótesis de una ventaja quantum-like no puede recibir soporte ni ser refutada.** El benchmark funciona como software, pero no discrimina entre el modelo quantum-like y los baselines clásicos. Todos los datos son sintéticos.

## Contexto de la ejecución

| | |
|---|---|
| Fecha | 2026-10-06 y 2026-10-07 |
| Rama | `research/programa-cuantico-2026` |
| Commit auditado | `c7771bb` (docs: add S002 generator recovery protocol) |
| Sistema | Linux 7.0 (Ubuntu), 4 núcleos |
| Python | 3.12.3, entorno virtual dedicado fuera del repositorio |
| Dependencias | numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2, pytest 9.1.1 |

No se instalaron `jupyter`, `ipywidgets`, `black` ni `mypy`: ningún test ni módulo los importa.

### Comandos

```bash
python -m pytest -q                                   # recoge test/ y tests/
python gui.py                                         # paneles ejercitados sin mostrar la ventana
python examples/simulador_indeterminacion.py
python -c "from saussure_quantum.s002_benchmark import matriz_recuperacion_s002; ..."
```

Los scripts de la batería S002 (matriz de recuperación, sensibilidad, robustez, optimizador) usan sólo funciones públicas de `s002_benchmark` con las semillas por defecto; los resultados de este documento se regeneran con `matriz_recuperacion_s002(n_replicas=50, n_por_orden=N)` y `evaluar_recuperacion_s002(..., ruido=r)`.

## Tests

| Momento | Resultado |
|---|---|
| Suite original, sin tocar código | **42 de 48** (6 fallos, todos en `test/test_uncertainty.py`) |
| Suite final, tras las correcciones | **163 de 163** |

Ningún test se desactivó ni se marcó `skip`/`xfail`. Sin warnings de NumPy ni de SciPy en la suite ni en las 3 950 réplicas de la batería S002 (cada una ajusta tres modelos desde varios arranques).

### Los 6 fallos originales

| Test | Clasificación | Causa raíz |
|---|---|---|
| `test_incertidumbre_estado_base` | Test incorrecto | Exigía ΔP > 1 y ΔS·ΔP ≥ ℏ/2. Para un estado base ΔS = 0 y ΔP = ℏ/√2 exactamente, producto 0. La cota ℏ/2 es falsa en dimensión finita. |
| `test_estado_minima_incertidumbre` | Test incorrecto | Misma cota: el estado gaussiano tiene producto 0.4876 < 0.5 sin violar nada. |
| `test_analizar_estado`, `test_incertidumbre_saussure_heisenberg` | Test desactualizado | La clave `satisface_principio` se había renombrado a `satisface_robertson`. |
| `test_demostrar_principio` | Test incorrecto | Suponía que el sintagma puro tiene producto "infinito o muy grande". Vale 0. |
| `test_paradoja_observador` | Implementación + test | El resultado era `np.bool_`, no `bool`; además usaba dimensión 2, donde el operador paradigma estaba mal construido. |

Los cuatro tests "incorrectos" se reescribieron con los valores analíticos y la desigualdad de Robertson. No se relajó ninguna tolerancia ni se cambió un resultado esperado para acomodar al código: lo que se cambió es una afirmación matemática falsa.

## Estado por componente

### VALIDADO

| Componente | Qué se comprobó |
|---|---|
| **Estados (2.1)** | Norma 1, traza 1, hermiticidad, ρ² = ρ y Σp = 1 en dimensiones 1, 2, 3, 7 y 50 con amplitudes complejas. Fase relativa correcta e invariante ante fase global. Base canónica ortonormal. Frecuencias de colapso (0.170, 0.168, 0.662) frente a (0.167, 0.167, 0.667) con 2·10⁴ muestras. |
| **Colapso y contexto (2.2)** | Misma semilla + mismo estado + mismo contexto → mismo resultado y mismas probabilidades. La temperatura afila o aplana como p^(1/T). `medicion_debil` reduce la entropía de forma monótona, conserva las fases relativas y sigue documentada como heurística, no como medición débil POVM/Kraus. |
| **Operadores (2.3)** | D = d·I − J es hermítica, con autovalores 0 y d (degeneración d−1), e igual a d·(I − \|u⟩⟨u\|). No muta las entradas. La diferencia por pares y el operador matricial dan resultados distintos y están documentados como no equivalentes. |
| **Robertson (2.4)** | ΔS·ΔP ≥ ½\|⟨[S,P]⟩\| sobre 12 577 estados (base, ondas planas, uniforme, aleatorios reales y complejos; d de 3 a 16): 0 violaciones. Tr[S,P] = 0 en toda dimensión, de modo que [S,P] = iℏI es imposible; la documentación mantiene esa limitación. |
| **S001 (2.5)** | El contexto diagonal coincide con el baseline clásico (diferencia máxima 5.6e-16 en 500 casos) y su efecto de orden es 0 (7.5e-16). Con G_A = X y G_B = Z sobre \|+⟩: AB = (0.5, 0.5), BA = (1, 0), L1 = 1. |
| **S002 — software** | Datos reproducibles por semilla; probabilidades válidas en los cuatro modelos; split exacto (train + test = original) en 50/50, 70/30, 80/20 y 90/10; los tres optimizadores alcanzan el óptimo global. |
| **Reproducibilidad** | Dos ejecuciones completas de la matriz de recuperación con las mismas semillas dan conteos idénticos. |
| **GUI y ejemplos** | Los 16 manejadores de los cinco paneles se ejecutan sin error; el ejemplo del simulador corre completo. |

### VALIDADO PARCIALMENTE

| Componente | Alcance y límite |
|---|---|
| **S002 — recuperación de modelo** | El procedimiento recupera la *clase observacional* correcta cuando el efecto es grande, pero no puede distinguir dos de las cuatro familias entre sí (ver sección S002). |
| **`paradoja_del_observador_linguistico`** | Calcula bien las dispersiones. Proyecta sobre el autovector más probable en lugar de muestrear, y con autovalores degenerados de P (p. ej. d = 4) el autovector elegido depende de la base de LAPACK. |
| **Función de Wigner** | Suma 1 y reproduce la marginal en x para toda dimensión. La marginal en p sólo es correcta para dimensión impar; en dimensión par no existe una función de Wigner d×d con ambas marginales. |

### NO VALIDADO

- **H7 (valor añadido del modelo quantum-like).** S002 no puede evaluarla: ver la sección siguiente.
- **Cualquier afirmación sobre lenguaje o cognición reales.** No hay datos humanos en el repositorio.
- **`docs/teoria_fusion.pdf`** y la "tesis central" del README son posiciones interpretativas; no se contrastan con ningún experimento.
- Los notebooks citados en `bug_report.md` no están en la rama y no se evaluaron.

### BLOQUEADO POR DEPENDENCIA EXTERNA

- Ninguno. El paquete no usa servicios externos. El extra opcional `qiskit` no se instaló ni se usa en el código.

## Resultados matemáticos

1. **No existe la cota ℏ/2.** En dimensión finita el estado base tiene ΔS = 0, ΔP = ℏ/√2 y producto 0. La desigualdad válida es la de Robertson, cuya cota depende del estado y puede ser 0. El README, la guía rápida, la referencia de API, la GUI y un ejemplo afirmaban que ΔS·ΔP "nunca puede ser menor que ℏ/2".
2. **El operador paradigma no era hermítico en dimensión 1 y 2.** Con borde periódico los vecinos i+1 e i−1 coinciden y la segunda asignación pisaba la primera: P = iℏ/2·X, anti-hermítica, con autovalores ±i/2. Los valores esperados imaginarios se truncaban con `.real`. Correcto: P = 0 (las contribuciones se cancelan). Ahora se acumulan y se avisa de que el análisis es trivial para d < 3.
3. **Ni el estado "de mínima incertidumbre" ni el "de máxima incertidumbre" hacen honor a su nombre.** El gaussiano tiene un producto *mayor* que los dos estados puros (0.449 frente a 0 en d = 10). La superposición uniforme es la onda plana de modo 0: ΔP = 0, producto 0.
4. **La derivación del operador D era errónea.** El docstring escribía D\|ψ⟩ = d\|ψ⟩ − Σ_j \|e_j⟩⟨e_j\|ψ⟩, pero esa suma es la identidad y daría (d−1)\|ψ⟩. D es el laplaciano del grafo completo: (Dψ)_i = Σ_j(ψ_i − ψ_j).
5. **`medir_diferencia` colapsaba mal.** El autovalor d está degenerado d−1 veces y se colapsaba a un autovector arbitrario de `eigh`: para \|x⟩ en d = 3 el estado posterior tenía probabilidades (0.26, 0.65, 0.09) o (0.41, 0.01, 0.58) según el caso. La regla de Lüders da (2/3, 1/6, 1/6). Las probabilidades de los *autovalores* sí eran correctas (0.3285 frente a 1/3).
6. **La diferencia por pares depende del orden.** Σ_{i<j}(ψ_i − ψ_j) = Σ_k (n−1−2k)ψ_k: con tres estados el del medio recibe coeficiente 0. `normalizar=False` no tiene efecto porque `SignoCuanto` normaliza siempre.
7. **`negatividad_total` es la constante d − 1** para todo estado normalizado; no distingue estados.
8. **La función de Wigner sumaba 2** y no reproducía la marginal en p.
9. **[A,B] ≠ 0 no implica efecto de orden observable.** Con X y Z, el estado \|+⟩ da L1 = 1 y el estado \|0⟩ da L1 = 0.

## S001

Validado como control. El modelo "quantum-like" diagonal es idéntico al baseline clásico, como anticipa la hipótesis H2 del documento S001. El control unitario muestra que el formalismo puede producir efectos de orden; no muestra que el significado los tenga ni que un modelo clásico no pueda producirlos.

## S002

### Resultado analítico: qué puede distinguir el diseño

Los datos son binarios y se observan dos órdenes. Hay exactamente **dos números observables**: p_AB y p_BA. Con el control \|+⟩, G_A = X, G_B = Z:

| Familia | Predicción | Parámetros declarados | Dimensión real |
|---|---|---:|---:|
| Clásico estático | p_AB = p_BA | 1 | 1 |
| Clásico secuencial | cualquier par (p_AB, p_BA) | 5 | **2** |
| Vectorial unitario | p_AB ≡ ½; p_BA[0] = (1 + sin 2θ_A·sin 2θ_B)/2 | 2 | **1** |
| Quantum-like | p_AB ≡ ½; p_BA[0] = (1 + (1−r)·sin 2θ_A·sin 2θ_B)/2 | 3 | **1** |

Tres consecuencias, todas verificadas numéricamente (`tests/test_s002_identificabilidad.py`):

1. **El modelo clásico secuencial es el modelo saturado.** Con canales constantes alcanza cualquier par de distribuciones; su verosimilitud ajustada coincide con la saturada (1429.7603 en ambos casos, split 80/20). Ningún modelo puede ajustar mejor estos datos.
2. **Vectorial y quantum-like son la misma familia observable.** \|+⟩ es autovector de X y U_B es diagonal, así que p_AB = ½ para todo θ (error máximo 9e-16 en 2 000 puntos). El ruido r sólo reescala un producto que ya recorre [−1, 1]: no es identificable.
3. **El punto sin efecto de orden (½, ½) pertenece a las tres familias.**

### Benchmark train/test (dataset por defecto, semilla 2026, 2 000 por orden)

| Split | Modelo | LL train | AIC train | BIC train | BIC efectivo | LL test | L1 test | JS test |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 80/20 | clásico estático | −1890.185 | 3782.37 | 3788.44 | 3788.44 | −487.4888 | 0.4618 | 0.037074 |
| | clásico secuencial | −1429.760 | 2869.52 | 2899.88 | 2875.66 | **−376.8279** | 0.0439 | 0.000524 |
| | vectorial unitario | −1429.805 | 2863.61 | **2875.75** | **2867.68** | −376.9967 | 0.0477 | 0.000577 |
| | quantum-like | −1429.805 | 2865.61 | 2883.83 | **2867.68** | −376.9967 | 0.0477 | 0.000577 |

En los otros splits el patrón es el mismo. El ganador por verosimilitud de test es el clásico secuencial en 70/30, 80/20 y 90/10. En 50/50 el procedimiento original declaraba ganador a **quantum-like** por una diferencia de 1e-9 con el vectorial: ruido del optimizador. Con detección de empates el resultado es "vectorial y quantum-like empatados". El BIC nominal elige siempre el vectorial; con parámetros efectivos, vectorial y quantum-like empatan exactamente.

El dataset por defecto se genera con AB = (0.50, 0.50) y BA = (0.95, 0.05), es decir, **dentro de la familia unitaria**. Que esa familia ajuste bien es una propiedad del generador, no un hallazgo.

### Benchmark con parámetros fijos (`benchmark_s002`)

LL: estático −2772.6, secuencial −2860.3, vectorial −4370.4, quantum-like −1832.6. El quantum-like "gana" porque sus valores por defecto (BA = 0.975, 0.025) están junto al generador, los del secuencial son arbitrarios y el vectorial predice probabilidad 0 para un resultado que ocurre 106 veces. No es una comparación de familias y así queda documentado en la función.

### Matriz de recuperación

50 réplicas, 1 000 observaciones por orden, split 80/20. Filas: régimen generador. Columnas: modelo seleccionado.

**Por verosimilitud de test**

| Generador | estático | secuencial | vectorial | quantum-like | Recuperación estricta |
|---|---:|---:|---:|---:|---:|
| sin_orden | **19** | 11 | 13 | 7 | 0.38 |
| clasico_secuencial | 11 | **32** | 5 | 2 | 0.64 |
| vectorial_unitario | 0 | 20 | **30** | 0 | 0.60 |
| quantum_like | 0 | 23 | 19 | **8** | 0.16 |

**Por BIC nominal (parámetros declarados)**

| Generador | estático | secuencial | vectorial | quantum-like | Recuperación estricta |
|---|---:|---:|---:|---:|---:|
| sin_orden | **50** | 0 | 0 | 0 | 1.00 |
| clasico_secuencial | 50 | **0** | 0 | 0 | 0.00 |
| vectorial_unitario | 0 | 0 | **50** | 0 | 1.00 |
| quantum_like | 0 | 0 | 50 | **0** | 0.00 |

**Por BIC efectivo (dimensión real de cada familia)**

| Generador | estático | secuencial | vectorial | quantum-like | Recuperación de la clase |
|---|---:|---:|---:|---:|---:|
| sin_orden | **25** | 0 | 15 | 10 | 0.50 |
| clasico_secuencial | 37 | **13** | 0 | 0 | 0.26 |
| vectorial_unitario | 0 | 1 | **49** | 0 | 0.98 |
| quantum_like | 0 | 0 | 28 | **22** | 1.00 |

Lectura:

- **Falsos negativos del régimen quantum-like.** El BIC nominal no lo recupera nunca (0 de 50, en todos los tamaños muestrales y niveles de ruido): misma verosimilitud que el vectorial y un parámetro más. Con BIC efectivo la selección entre vectorial y quantum-like es un sorteo (28/22), porque empatan en las 50 réplicas.
- **Confusión vectorial / quantum-like.** Total. La diferencia máxima de log-verosimilitud de test entre ambos, en 1 000 ajustes, es 4.9e-6.
- **Confusión clásico secuencial / quantum-like.** Cuando el generador es unitario, la verosimilitud de test elige el modelo clásico secuencial entre el 32 % y el 54 % de las réplicas según el tamaño muestral, sin tendencia a bajar con más datos (el saturado también contiene la verdad y el holdout apenas penaliza un grado de libertad extra).
- **Falsos positivos.** Sin efecto de orden, la verosimilitud de test elige un modelo unitario en el 40 % de las réplicas y el BIC efectivo en el 50 %: (½, ½) pertenece a esa familia. El BIC nominal "acierta" 50 de 50 sólo porque sobrepenaliza a las familias unitarias con parámetros que no son identificables.
- **Un defecto de la métrica original**: la recuperación de `sin_orden` daba 0.00 por construcción, porque se buscaba el nombre del régimen entre nombres de modelos. Corregido.

### Sensibilidad al tamaño muestral

Recuperación de la clase observacional correcta (50 réplicas por celda).

| Generador | Criterio | n=100 | 500 | 1 000 | 2 000 | 5 000 |
|---|---|---:|---:|---:|---:|---:|
| clasico_secuencial | test LL | 0.34 | 0.62 | 0.64 | 0.78 | 0.84 |
| (L1 entre órdenes = 0.10) | BIC nominal | 0.00 | 0.00 | 0.00 | 0.02 | 0.04 |
| | BIC efectivo | 0.00 | 0.12 | 0.26 | 0.64 | 0.96 |
| vectorial_unitario | test LL | 0.56 | 0.68 | 0.60 | 0.54 | 0.60 |
| | BIC nominal | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| quantum_like (clase) | test LL | 0.52 | 0.46 | 0.54 | 0.62 | 0.60 |
| | BIC efectivo | 0.96 | 0.98 | 1.00 | 1.00 | 1.00 |
| quantum_like (estricta) | BIC nominal | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| sin_orden | test LL | 0.40 | 0.24 | 0.38 | 0.36 | 0.32 |
| | BIC efectivo | 0.52 | 0.68 | 0.50 | 0.56 | 0.68 |

Sólo la recuperación del régimen clásico secuencial mejora con el tamaño muestral. Las demás están limitadas por la estructura del diseño, no por la cantidad de datos.

### Robustez: tamaño del efecto

**Efecto dentro de la familia unitaria** (p_AB = 0.5, p_BA[0] = 0.5 + δ). Réplicas de 50 que seleccionan la clase unitaria con BIC nominal:

| δ | L1 | n=200 | n=1 000 | n=5 000 |
|---:|---:|---:|---:|---:|
| 0.00 | 0.00 | 0 | 0 | 0 |
| 0.02 | 0.04 | 0 | 0 | 8 |
| 0.05 | 0.10 | 1 | 12 | 44 |
| 0.10 | 0.20 | 13 | 44 | 50 |
| 0.20 | 0.40 | 41 | 50 | 50 |
| 0.45 | 0.90 | 50 | 50 | 50 |

El efecto se detecta de forma fiable (≥ 80 %) cuando δ·√n ≳ 3: δ ≈ 0.20 con n = 200, 0.10 con n = 1 000 y 0.05 con n = 5 000. Por debajo, el problema deja de ser identificable y el resultado correcto es "sin efecto detectable".

**Efecto fuera de la familia unitaria** (p_AB[0] = 0.5 − ε, p_BA[0] = 0.5 + ε; sólo el modelo saturado es correcto). Réplicas de 50 por clase, BIC nominal → BIC efectivo:

| ε | n | estático | saturado | unitario |
|---:|---:|---:|---:|---:|
| 0.05 | 1 000 | 32 → 1 | 1 → 30 | **17 → 19** |
| 0.10 | 200 | 29 → 1 | 0 → 27 | **21 → 22** |
| 0.035 | 5 000 | 5 → 0 | 13 → 48 | **32 → 2** |
| 0.10 | 1 000 | 0 → 0 | 40 → 50 | 10 → 0 |
| 0.20 | 200 | 0 → 0 | 40 → 50 | 10 → 0 |

Este es el falso positivo que más importa: con datos generados por un proceso que **no** es unitario, el procedimiento elige la clase unitaria (vectorial/quantum-like) entre el 34 % y el 64 % de las veces en la zona de potencia intermedia. Con BIC nominal ocurre incluso con 5 000 observaciones por orden, porque el modelo correcto carga con cinco parámetros declarados.

### Robustez: ruido del régimen quantum-like

n = 1 000 por orden, 50 réplicas.

| Ruido r | p_BA verdadera | Recuperación estricta (BIC nominal) | Recuperación de clase (BIC efectivo) |
|---:|---|---:|---:|
| 0.00 – 0.75 | (1.00, 0.00) a (0.625, 0.375) | 0.00 | 0.98 |
| 0.90 | (0.55, 0.45) | 0.00 | 0.92 |
| 0.95 | (0.525, 0.475) | 0.00 | 0.68 |
| 0.99 | (0.505, 0.495) | 0.00 | 0.46 |
| 1.00 | (0.50, 0.50) | 0.00 | 0.48 |

El ruido no cambia la identificabilidad del modelo quantum-like frente al vectorial (nula en todo el rango); sólo reduce el tamaño del efecto. Con r ≥ 0.9 el efecto cae por debajo del umbral de detección y el régimen se confunde con "sin orden".

### Optimización

200 arranques aleatorios por modelo sobre el dataset por defecto.

| Modelo | Arranques en el óptimo global | Peor NLL | `success` de BFGS | Dispersión de los parámetros en el óptimo |
|---|---:|---:|---:|---|
| clásico secuencial | 97.0 % | 2377.5 | 10 / 200 | 3.9 a 7.5 por coordenada |
| vectorial unitario | 100 % | 1806.55 | 8 / 200 | 3.7 y 3.9 |
| quantum-like | 100 % | 1806.55 | 6 / 200 | 3.0, 3.1 y 9.7 |

- Los tres arranques deterministas del código alcanzan el óptimo global en todos los casos probados.
- BFGS casi nunca declara `success`: termina por pérdida de precisión, porque la superficie es plana en las direcciones no identificables. El valor del óptimo es correcto; **los parámetros ajustados no son interpretables**. Un mismo óptimo se alcanza con parámetros dispersos en un rango de varias unidades.
- El modelo secuencial tiene mínimos locales: un 3 % de los arranques aleatorios queda en una meseta (sigmoides saturadas). Los arranques múltiples del código lo evitan.

## Auditoría científica

**1. ¿S002 recupera los modelos generadores?** Parcialmente. Recupera la *clase* unitaria cuando el efecto es grande y la clase saturada cuando hay muchos datos. No recupera el régimen quantum-like como tal en ninguna condición.

**2. ¿El modelo clásico secuencial puede explicar los efectos de orden?** Sí, todos. Es el modelo saturado para este diseño: reproduce cualquier par de distribuciones binarias.

**3. ¿Quantum-like aporta algo que el baseline clásico no explique?** No en este diseño. Su familia observable es un subconjunto de la del clásico secuencial e idéntica a la del vectorial sin ruido.

**4. ¿La ventaja depende de un régimen particular?** No hay ventaja que medir. Lo que sí depende del régimen es el BIC: los modelos unitarios obtienen mejor BIC sólo cuando el generador cumple p_AB = ½, que es la restricción que el control X/Z impone por construcción.

**5. ¿Hay equivalencias observacionales?** Tres: vectorial ≡ quantum-like (exacta, siempre); clásico secuencial ⊇ todas las demás; y estático ∩ unitario en el punto sin efecto de orden.

**6. ¿La recuperación cambia con el tamaño muestral?** Sólo para el régimen clásico secuencial (0.00 → 0.96 con BIC efectivo entre n = 100 y 5 000). La confusión vectorial/quantum-like y la tasa de selección del saturado bajo generador unitario no cambian.

**7. ¿La recuperación cambia con el ruido?** La recuperación estricta de quantum-like es 0.00 en todo el rango. La de su clase se mantiene en 0.98 hasta r = 0.75 y se pierde a partir de r ≈ 0.9.

**8. ¿Hay problemas de identificabilidad?** Sí, y son estructurales: dos observables frente a 5, 2 y 3 parámetros declarados. Los parámetros efectivos son 2, 1 y 1.

**9. ¿Los resultados son reproducibles?** Sí. Semillas fijas; dos ejecuciones dan conteos idénticos.

**10. ¿Qué afirmaciones de la documentación están respaldadas?**
- "La mera existencia de AB ≠ BA no demuestra una ventaja quantum-like" (S002): respaldada, y con más fuerza de la que el documento suponía.
- "El modelo clásico secuencial puede estar débilmente identificado" (S002): respaldada; de hecho es saturado.
- "Para filtros diagonales el modelo quantum-like no supera al baseline" (S001): respaldada, son idénticos.
- "[S,P] = iℏI es imposible en dimensión finita": respaldada.
- "`medicion_debil` es heurística": respaldada.

**11. ¿Qué afirmaciones deben debilitarse?** Ya corregidas en esta auditoría:
- "ΔS·ΔP nunca puede ser menor que ℏ/2" → falso; sustituido por Robertson.
- "demuestra isomorfías profundas" (README) → "propone analogías formales".
- "Estado de mínima / máxima incertidumbre" → nombres históricos; no minimizan ni maximizan.
- La tabla de complejidad de S002 (5, 2 y 3 parámetros) → ahora acompañada de la dimensión real.
- "Quantum-like: dinámica unitaria + ruido/decoherencia efectiva" como modelo distinto del vectorial → no lo es con estos datos.

Queda pendiente de decisión editorial la "tesis central" del README ("la realidad no es una sustancia…"): es una posición filosófica, no un resultado, y convendría presentarla como tal.

**12. ¿Qué experimento debe hacerse después?** Ver la sección siguiente.

## Bajo qué condiciones la hipótesis sería falsable

La hipótesis quantum-like sobre efectos de orden hace una predicción sin parámetros libres que un modelo clásico de Markov no hace: la **igualdad QQ** (Wang y Busemeyer, 2013). Si se registran las dos respuestas en cada orden, un modelo proyectivo exige

    p(A sí, B no) + p(A no, B sí)   en el orden A→B
  = p(B sí, A no) + p(B no, A sí)   en el orden B→A.

Un modelo clásico secuencial genérico viola esa igualdad. Ese diseño tiene tres observables libres por orden en lugar de uno, y ahí el modelo quantum-like puede **fallar**: es falsable.

## Próximos experimentos

1. **S003 — diseño con respuestas conjuntas e igualdad QQ.** Registrar las dos respuestas por orden (cuatro resultados por orden). Antes de usar datos reales: repetir la recuperación de modelo y exigir que el régimen clásico de Markov sea rechazado por el test QQ y el régimen proyectivo no.
2. **Análisis de potencia previo.** Con la regla empírica de esta auditoría (efecto detectable cuando δ·√n ≳ 3), fijar el tamaño muestral antes de recolectar.
3. **Sustituir la selección por holdout** entre modelos anidados por un contraste de razón de verosimilitud o validación cruzada repetida: con una sola partición 80/20 la selección del modelo correcto se estanca en torno al 60 %.
4. **Más de dos contextos o dimensión mayor que 2**, de forma que el modelo clásico deje de ser saturado.
5. **Reparametrizar o retirar el modelo quantum-like con ruido** mientras los datos no permitan identificar r; mantenerlo sólo si el diseño incluye una condición que lo separe del vectorial.

## Actualización: S003 (2026-10-07)

Los "próximos experimentos" 1 a 3 de la sección anterior se ejecutaron como S003. Resumen; el detalle está en [`docs/RESULTADOS_S003.md`](RESULTADOS_S003.md).

| Etiqueta | Resultado |
|---|---|
| VALIDADO MATEMÁTICAMENTE | Todo modelo proyectivo cumple la igualdad QQ; el modelo clásico de repetición simétrica también. |
| VALIDADO COMPUTACIONALMENTE | El test de QQ tiene nivel 0.043–0.056 y la potencia analítica; el Markov clásico de dos estados es saturado; las cotas de Cauchy–Schwarz delimitan lo alcanzable por un modelo proyectivo. |
| NO IDENTIFICABLE | Clase clásica frente a clase proyectiva; fase, pureza, dimensión y rango del modelo proyectivo. |
| RESULTADO NEGATIVO | La igualdad QQ no discrimina modelos clásicos de quantum-like. |
| RESULTADO POSITIVO | QQ y las cotas son predicciones falsables del modelo proyectivo; el diseño de respuestas conjuntas recupera la familia generadora con n ≈ 5 000 por orden. |
| EVIDENCIA EMPÍRICA | Ninguna. |
| NO TESTEADO | Datos humanos. |

Una corrección a este mismo documento: la sección "Bajo qué condiciones la hipótesis sería falsable" decía que el diseño QQ permitiría separar el modelo quantum-like del clásico de Markov. S003 muestra que sólo lo separa del Markov *genérico*; un modelo clásico restringido cumple QQ y el Markov general reproduce cualquier distribución proyectiva. El texto original se conserva como registro.

Regresión tras incorporar S003: 296 tests (163 previos sin modificar + 133 de S003), todos pasan. S001 y S002 no se tocaron.

## Limitaciones de esta auditoría

- Todos los datos son sintéticos y generados por los propios modelos comparados.
- La batería de robustez usa 50 réplicas por celda: las proporciones tienen un error estándar de hasta 0.07.
- El análisis de identificabilidad vale para el control \|+⟩, X, Z con resultados binarios. Otros estados iniciales o generadores cambian las familias observables y habría que repetirlo.
- La GUI se ejercitó llamando a sus manejadores, sin inspección visual.
- `setup.py` declara `jupyter` e `ipywidgets` como dependencias de ejecución aunque el paquete no las usa, y conserva metadatos de plantilla (autor, URL). No se modificó.
