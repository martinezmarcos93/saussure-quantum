"""Benchmark S002: comparación de modelos para efecto de orden.

Genera datos sintéticos con una dinámica contextual secuencial conocida y
compara cuatro familias:
1. clásico estático;
2. clásico secuencial;
3. vectorial unitario con operadores potencialmente no conmutativos;
4. quantum-like equivalente al modelo unitario.

El benchmark es metodológico: un resultado favorable al modelo quantum-like
sólo es relevante si mejora ajuste/predicción fuera de muestra bajo una
penalización de complejidad razonable.

Identificabilidad (resultado analítico, verificado en tests/test_s002_identificabilidad.py)
---------------------------------------------------------------------------------------
Los datos son binarios y se observan sólo dos órdenes: hay exactamente DOS
números observables, (p_AB, p_BA). Con el control |+⟩, G_A = X, G_B = Z:

- clásico estático:   p_AB = p_BA = p.                    Familia de dimensión 1.
- clásico secuencial: alcanza cualquier par (p_AB, p_BA)   Familia de dimensión 2
  (basta tomar canales constantes): es el modelo SATURADO.  aunque declare 5 parámetros.
- vectorial unitario: p_AB ≡ 1/2 para todo θ (|+⟩ es autovector de X y U_B es
  diagonal), y p_BA[0] = (1 + sin 2θ_A · sin 2θ_B)/2.       Familia de dimensión 1.
- quantum-like:       p_AB ≡ 1/2, p_BA[0] = (1 + (1−r)·sin 2θ_A·sin 2θ_B)/2.
  Es EXACTAMENTE la misma familia que la vectorial: el ruido r no es identificable.

Consecuencias: (1) vectorial y quantum-like son observacionalmente equivalentes
en este diseño; cualquier "ganador" entre ellos por verosimilitud es ruido del
optimizador. (2) El modelo clásico secuencial reproduce cualquier dato binario
de dos órdenes, de modo que este diseño no puede mostrar una ventaja
quantum-like sobre él. (3) Los parámetros nominales (5, 2, 3) sobrestiman la
dimensión de cada familia; por eso se informa además un BIC con parámetros
efectivos. Los nominales se conservan para no alterar los resultados previos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

import numpy as np


@dataclass(frozen=True)
class S002Dataset:
    """Observaciones agrupadas por orden contextual."""

    counts_ab: np.ndarray
    counts_ba: np.ndarray

    @property
    def n_ab(self) -> int:
        return int(self.counts_ab.sum())

    @property
    def n_ba(self) -> int:
        return int(self.counts_ba.sum())


def _softmax(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    z = x - np.max(x)
    p = np.exp(z)
    return p / p.sum()


def generar_datos_s002(
    n_por_orden: int = 2000,
    seed: int = 2026,
    prob_ab: Iterable[float] = (0.50, 0.50),
    prob_ba: Iterable[float] = (0.95, 0.05),
) -> S002Dataset:
    """Genera un dataset binario con efecto de orden controlado."""
    if n_por_orden < 1:
        raise ValueError("n_por_orden debe ser >= 1.")
    p_ab = np.asarray(tuple(prob_ab), dtype=float)
    p_ba = np.asarray(tuple(prob_ba), dtype=float)
    for p in (p_ab, p_ba):
        if p.shape != (2,) or np.any(p < 0) or not np.isclose(p.sum(), 1):
            raise ValueError("Cada distribución debe tener dos probabilidades que sumen 1.")
    rng = np.random.default_rng(seed)
    return S002Dataset(
        rng.multinomial(n_por_orden, p_ab),
        rng.multinomial(n_por_orden, p_ba),
    )



REGIMENES_S002 = (
    "sin_orden",
    "clasico_secuencial",
    "vectorial_unitario",
    "quantum_like",
)

# Familia de modelos que corresponde a cada régimen generador. El régimen
# "sin_orden" se genera con el modelo clásico estático.
MODELO_DE_REGIMEN = {
    "sin_orden": "clasico_estatico",
    "clasico_secuencial": "clasico_secuencial",
    "vectorial_unitario": "vectorial_unitario",
    "quantum_like": "quantum_like",
}

# Parámetros declarados por cada familia (los usados históricamente en AIC/BIC).
N_PARAMS_NOMINALES = {
    "clasico_estatico": 1,
    "clasico_secuencial": 5,
    "vectorial_unitario": 2,
    "quantum_like": 3,
}

# Dimensión de la familia de distribuciones observables (p_AB, p_BA) que cada
# modelo puede producir: rango del jacobiano de la predicción respecto de los
# parámetros. Ver el docstring del módulo.
N_PARAMS_EFECTIVOS = {
    "clasico_estatico": 1,
    "clasico_secuencial": 2,
    "vectorial_unitario": 1,
    "quantum_like": 1,
}

# Familias que predicen exactamente el mismo conjunto de distribuciones.
CLASE_OBSERVACIONAL = {
    "clasico_estatico": "estatico",
    "clasico_secuencial": "saturado",
    "vectorial_unitario": "unitario_xz",
    "quantum_like": "unitario_xz",
}

# Diferencia de log-verosimilitud (o de BIC) por debajo de la cual dos modelos
# se consideran empatados. Muy inferior a cualquier diferencia estadísticamente
# relevante y muy superior al ruido del optimizador (~1e-6).
TOLERANCIA_EMPATE = 1e-3


def probabilidades_regimen_s002(
    regimen: str,
    ruido: float = 0.05,
) -> Tuple[np.ndarray, np.ndarray]:
    """Devuelve las probabilidades verdaderas de un régimen sintético."""
    if regimen == "sin_orden":
        return baseline_clasico_estatico()
    if regimen == "clasico_secuencial":
        return modelo_clasico_secuencial()
    if regimen == "vectorial_unitario":
        return modelo_vectorial_unitario()
    if regimen == "quantum_like":
        return modelo_quantum_like(ruido=ruido)
    raise ValueError(
        f"Régimen desconocido: {regimen!r}. "
        f"Opciones: {REGIMENES_S002}."
    )


def generar_datos_regimen_s002(
    regimen: str,
    n_por_orden: int = 2000,
    seed: int = 2026,
    ruido: float = 0.05,
) -> S002Dataset:
    """Genera datos sintéticos desde un modelo generador conocido."""
    p_ab, p_ba = probabilidades_regimen_s002(regimen, ruido=ruido)
    return generar_datos_s002(
        n_por_orden=n_por_orden,
        seed=seed,
        prob_ab=p_ab,
        prob_ba=p_ba,
    )

def distribuciones_observadas(data: S002Dataset) -> Dict[str, np.ndarray]:
    """Devuelve las frecuencias empíricas por orden."""
    return {
        "AB": data.counts_ab / data.n_ab,
        "BA": data.counts_ba / data.n_ba,
    }


def distancia_l1(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.abs(np.asarray(p) - np.asarray(q)).sum())


def divergencia_kl(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    return float(np.sum(p * np.log((p + eps) / (q + eps))))


def divergencia_js(p: np.ndarray, q: np.ndarray) -> float:
    m = (np.asarray(p) + np.asarray(q)) / 2
    return 0.5 * divergencia_kl(p, m) + 0.5 * divergencia_kl(q, m)


def log_likelihood_multinomial(
    counts: np.ndarray,
    probabilities: np.ndarray,
    eps: float = 1e-12,
) -> float:
    """Log-verosimilitud multinomial ignorando la constante combinatoria."""
    counts = np.asarray(counts, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    return float(np.sum(counts * np.log(np.clip(probabilities, eps, 1))))


def aic(log_likelihood: float, n_params: int) -> float:
    return float(2 * n_params - 2 * log_likelihood)


def bic(log_likelihood: float, n_params: int, n_obs: int) -> float:
    return float(n_params * np.log(n_obs) - 2 * log_likelihood)


def evaluar_predicciones(
    data: S002Dataset,
    predicciones: Dict[str, Tuple[np.ndarray, np.ndarray]],
    n_params: Dict[str, int],
) -> Dict[str, Dict[str, float]]:
    """Calcula métricas homogéneas para cada modelo."""
    obs = distribuciones_observadas(data)
    resultados: Dict[str, Dict[str, float]] = {}

    for nombre, (p_ab, p_ba) in predicciones.items():
        ll = (
            log_likelihood_multinomial(data.counts_ab, p_ab)
            + log_likelihood_multinomial(data.counts_ba, p_ba)
        )
        l1 = 0.5 * (distancia_l1(obs["AB"], p_ab) + distancia_l1(obs["BA"], p_ba))
        js = 0.5 * (divergencia_js(obs["AB"], p_ab) + divergencia_js(obs["BA"], p_ba))
        resultados[nombre] = {
            "L1_medio": l1,
            "JS_medio": js,
            "log_likelihood": ll,
            "AIC": aic(ll, n_params[nombre]),
            "BIC": bic(ll, n_params[nombre], data.n_ab + data.n_ba),
        }
    return resultados


def baseline_clasico_estatico(
    p: Iterable[float] = (0.5, 0.5),
) -> Tuple[np.ndarray, np.ndarray]:
    """Un único estado probabilístico para ambos órdenes."""
    p = np.asarray(tuple(p), dtype=float)
    if p.shape != (2,) or np.any(p < 0) or not np.isclose(p.sum(), 1):
        raise ValueError("p debe ser una distribución binaria.")
    return p.copy(), p.copy()


def modelo_clasico_secuencial(
    p0: Iterable[float] = (0.5, 0.5),
    matriz_a: np.ndarray | None = None,
    matriz_b: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo clásico dinámico: cada contexto es una transformación estocástica.

    Las matrices son canales de Markov por columnas: p' = M @ p.
    """
    p0 = np.asarray(tuple(p0), dtype=float)
    if matriz_a is None:
        matriz_a = np.array([[0.9, 0.2], [0.1, 0.8]])
    if matriz_b is None:
        matriz_b = np.array([[0.7, 0.1], [0.3, 0.9]])
    for m in (matriz_a, matriz_b):
        if m.shape != (2, 2) or np.any(m < 0) or not np.allclose(m.sum(axis=0), 1):
            raise ValueError("Los canales clásicos deben ser matrices estocásticas por columnas.")
    return matriz_b @ matriz_a @ p0, matriz_a @ matriz_b @ p0


def modelo_vectorial_unitario(
    amplitud_inicial: Iterable[complex] = (1 / np.sqrt(2), 1 / np.sqrt(2)),
    generador_a: np.ndarray | None = None,
    generador_b: np.ndarray | None = None,
    theta_a: float = np.pi / 4,
    theta_b: float = np.pi / 4,
) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo vectorial unitario; conserva fases pero no usa la semántica de rho.

    Con los valores por defecto (|+⟩, G_A = X, G_B = Z) la predicción es
    p_AB = (1/2, 1/2) para todo θ y p_BA[0] = (1 + sin 2θ_A · sin 2θ_B)/2:
    sólo el producto sin 2θ_A · sin 2θ_B es identificable.
    """
    from scipy.linalg import expm

    psi = np.asarray(tuple(amplitud_inicial), dtype=complex)
    if psi.shape != (2,) or not np.isclose(np.linalg.norm(psi), 1):
        raise ValueError("La amplitud inicial debe ser un vector binario normalizado.")
    if generador_a is None:
        generador_a = np.array([[0, 1], [1, 0]], dtype=complex)
    if generador_b is None:
        generador_b = np.array([[1, 0], [0, -1]], dtype=complex)
    for g in (generador_a, generador_b):
        if g.shape != (2, 2) or not np.allclose(g, g.conj().T):
            raise ValueError("Los generadores deben ser Hermitianos.")
    ua = expm(-1j * theta_a * generador_a)
    ub = expm(-1j * theta_b * generador_b)
    p_ab = np.abs(ub @ ua @ psi) ** 2
    p_ba = np.abs(ua @ ub @ psi) ** 2
    return p_ab, p_ba


def modelo_quantum_like(
    ruido: float = 0.05,
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo quantum-like con estado puro y decoherencia efectiva.

    La mezcla se modela como un canal de ruido clásico sobre las
    probabilidades de medición:
        p' = (1-r) p + r / d.

    Es deliberadamente simple: permite separar el control vectorial puro
    de una representación que admite pérdida de coherencia/indeterminación.

    Limitación: con datos binarios de dos órdenes el ruido NO es identificable.
    La predicción p_BA[0] = (1 + (1−r)·sin 2θ_A·sin 2θ_B)/2 recorre el mismo
    intervalo [0, 1] que el modelo vectorial, y p_AB sigue siendo 1/2. Ambas
    familias son observacionalmente equivalentes en este diseño.
    """
    if not 0 <= ruido <= 1:
        raise ValueError("ruido debe estar en [0, 1].")
    p_ab, p_ba = modelo_vectorial_unitario(**kwargs)
    uniform = np.full_like(p_ab, 1.0 / len(p_ab))
    return (
        (1 - ruido) * p_ab + ruido * uniform,
        (1 - ruido) * p_ba + ruido * uniform,
    )



def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    """Transformación logística estable para parámetros acotados."""
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def dividir_train_test(
    data: S002Dataset,
    proporcion_train: float = 0.8,
    seed: int = 2026,
) -> Tuple[S002Dataset, S002Dataset]:
    """Divide cada orden mediante un muestreo binomial reproducible."""
    if not 0 < proporcion_train < 1:
        raise ValueError("proporcion_train debe estar estrictamente entre 0 y 1.")
    rng = np.random.default_rng(seed)
    train, test = [], []
    for counts in (data.counts_ab, data.counts_ba):
        n0 = int(rng.binomial(int(counts[0]), proporcion_train))
        n1 = int(rng.binomial(int(counts[1]), proporcion_train))
        tr = np.array([n0, n1], dtype=int)
        train.append(tr)
        test.append(np.asarray(counts, dtype=int) - tr)
    return S002Dataset(train[0], train[1]), S002Dataset(test[0], test[1])


def _nll_dataset(data: S002Dataset, predicciones: Tuple[np.ndarray, np.ndarray]) -> float:
    return -(
        log_likelihood_multinomial(data.counts_ab, predicciones[0])
        + log_likelihood_multinomial(data.counts_ba, predicciones[1])
    )


def _optimizar(objetivo: Callable[[np.ndarray], float], x0s: Iterable[np.ndarray]) -> np.ndarray:
    """Minimiza desde varios puntos iniciales deterministas."""
    from scipy.optimize import minimize

    resultados = []
    for x0 in x0s:
        r = minimize(objetivo, np.asarray(x0, dtype=float), method="BFGS",
                     options={"maxiter": 2000, "gtol": 1e-8})
        if np.isfinite(r.fun):
            resultados.append(r)
    if not resultados:
        raise RuntimeError("No fue posible ajustar el modelo.")
    return np.asarray(min(resultados, key=lambda r: r.fun).x, dtype=float)


def ajustar_clasico_estatico(data: S002Dataset) -> Tuple[np.ndarray, np.ndarray]:
    """Ajusta una probabilidad compartida a ambos órdenes."""
    total = data.counts_ab + data.counts_ba
    p1 = float(total[1] / total.sum())
    p = np.array([1.0 - p1, p1])
    return p.copy(), p.copy()


def ajustar_clasico_secuencial(data: S002Dataset) -> Tuple[np.ndarray, np.ndarray]:
    """Ajusta estado inicial y dos canales estocásticos binarios."""
    def pred(x):
        p0 = float(_sigmoid(x[0]))
        a0, a1, b0, b1 = map(float, _sigmoid(x[1:]))
        p = np.array([1.0 - p0, p0])
        ma = np.array([[1.0 - a0, a1], [a0, 1.0 - a1]])
        mb = np.array([[1.0 - b0, b1], [b0, 1.0 - b1]])
        return mb @ ma @ p, ma @ mb @ p

    x = _optimizar(lambda z: _nll_dataset(data, pred(z)), (
        np.zeros(5),
        np.array([0.0, -1.0, 1.0, -1.0, 1.0]),
        np.array([0.0, 1.0, -1.0, 1.0, -1.0]),
    ))
    return pred(x)


def ajustar_vectorial_unitario(data: S002Dataset) -> Tuple[np.ndarray, np.ndarray]:
    """Ajusta theta_A y theta_B con generadores X/Z fijos."""
    def pred(x):
        return modelo_vectorial_unitario(theta_a=float(x[0]), theta_b=float(x[1]))

    x = _optimizar(lambda z: _nll_dataset(data, pred(z)), (
        np.array([np.pi / 4, np.pi / 4]),
        np.array([0.2, 0.8]),
        np.array([0.8, 0.2]),
        np.array([1.2, 1.2]),
    ))
    return pred(x)


def ajustar_quantum_like(data: S002Dataset) -> Tuple[np.ndarray, np.ndarray]:
    """Ajusta theta_A, theta_B y ruido efectivo."""
    def pred(x):
        return modelo_quantum_like(
            ruido=float(_sigmoid(x[2])),
            theta_a=float(x[0]),
            theta_b=float(x[1]),
        )

    x = _optimizar(lambda z: _nll_dataset(data, pred(z)), (
        np.array([np.pi / 4, np.pi / 4, -2.0]),
        np.array([0.2, 0.8, -1.0]),
        np.array([0.8, 0.2, 0.0]),
        np.array([1.2, 1.2, 1.0]),
    ))
    return pred(x)


def ajustar_modelos_s002(data_train: S002Dataset) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Ajusta todas las familias exclusivamente sobre train."""
    return {
        "clasico_estatico": ajustar_clasico_estatico(data_train),
        "clasico_secuencial": ajustar_clasico_secuencial(data_train),
        "vectorial_unitario": ajustar_vectorial_unitario(data_train),
        "quantum_like": ajustar_quantum_like(data_train),
    }


def evaluar_train_test_s002(train: S002Dataset, test: S002Dataset) -> Dict[str, Dict[str, float]]:
    """Ajusta en train y calcula predicción fuera de muestra en test."""
    pred = ajustar_modelos_s002(train)
    n_params = N_PARAMS_NOMINALES
    resultados = evaluar_predicciones(test, pred, n_params)
    n_train = train.n_ab + train.n_ba
    for nombre, (p_ab, p_ba) in pred.items():
        ll = (
            log_likelihood_multinomial(train.counts_ab, p_ab)
            + log_likelihood_multinomial(train.counts_ba, p_ba)
        )
        resultados[nombre]["log_likelihood_train"] = ll
        resultados[nombre]["AIC_train"] = aic(ll, n_params[nombre])
        resultados[nombre]["BIC_train"] = bic(ll, n_params[nombre], n_train)
        # Mismo criterio con la dimensión real de la familia observable.
        k_ef = N_PARAMS_EFECTIVOS[nombre]
        resultados[nombre]["AIC_train_efectivo"] = aic(ll, k_ef)
        resultados[nombre]["BIC_train_efectivo"] = bic(ll, k_ef, n_train)
    return resultados


def benchmark_ajustado_s002(
    data: S002Dataset | None = None,
    proporcion_train: float = 0.8,
    seed_split: int = 2026,
) -> Dict[str, Dict[str, float]]:
    """Ejecuta split, ajuste y evaluación fuera de muestra."""
    data = data or generar_datos_s002()
    train, test = dividir_train_test(data, proporcion_train, seed_split)
    return evaluar_train_test_s002(train, test)


def seleccionar_modelo_s002(
    resultados: Dict[str, Dict[str, float]],
    criterio: str = "test_log_likelihood",
) -> str:
    """Selecciona el modelo ganador según un criterio explícito.

    Devuelve siempre UN nombre. En caso de empate gana el primero en el orden
    del diccionario, y diferencias del orden del ruido del optimizador (~1e-6)
    bastan para decidir. Para saber si el ganador es distinguible de los demás
    usar `modelos_empatados_s002`.
    """
    clave, mayor_es_mejor = _clave_criterio(criterio)
    if not resultados:
        raise ValueError("resultados no puede estar vacío.")
    elegir = max if mayor_es_mejor else min
    return elegir(resultados, key=lambda n: resultados[n][clave])


_CRITERIOS_S002 = {
    "test_log_likelihood": ("log_likelihood", True),
    "test_L1": ("L1_medio", False),
    "test_JS": ("JS_medio", False),
    "train_BIC": ("BIC_train", False),
    "train_BIC_efectivo": ("BIC_train_efectivo", False),
}


def _clave_criterio(criterio: str) -> Tuple[str, bool]:
    if criterio not in _CRITERIOS_S002:
        raise ValueError(
            "criterio debe ser test_log_likelihood, test_L1, test_JS, "
            "train_BIC o train_BIC_efectivo."
        )
    return _CRITERIOS_S002[criterio]


def modelos_empatados_s002(
    resultados: Dict[str, Dict[str, float]],
    criterio: str = "test_log_likelihood",
    tolerancia: float = TOLERANCIA_EMPATE,
) -> Tuple[str, ...]:
    """Modelos indistinguibles del mejor según el criterio, en orden estable.

    Si devuelve más de un nombre, los datos no permiten elegir entre ellos y
    el resultado debe informarse como empate (equivalencia observacional o
    falta de información), no como una clasificación.
    """
    clave, mayor_es_mejor = _clave_criterio(criterio)
    if not resultados:
        raise ValueError("resultados no puede estar vacío.")
    if tolerancia < 0:
        raise ValueError("tolerancia debe ser >= 0.")
    valores = {n: r[clave] for n, r in resultados.items()}
    mejor = max(valores.values()) if mayor_es_mejor else min(valores.values())
    return tuple(n for n, v in valores.items() if abs(v - mejor) <= tolerancia)


def evaluar_recuperacion_s002(
    regimen: str,
    n_replicas: int = 20,
    n_por_orden: int = 1000,
    seed: int = 2026,
    proporcion_train: float = 0.8,
    ruido: float = 0.05,
) -> Dict[str, object]:
    """Evalúa con qué frecuencia el procedimiento recupera un régimen conocido.

    Esto no presupone que el régimen verdadero sea identificable: una baja
    recuperación es un resultado científico válido y puede revelar que dos
    familias son observacionalmente equivalentes con los datos disponibles.

    Además de la selección estricta (un único ganador, con desempate por orden)
    se informa:

    - `frecuencia_bic_efectivo`: selección por BIC con la dimensión real de
      cada familia (`N_PARAMS_EFECTIVOS`);
    - `empates_test` / `empates_bic_efectivo`: réplicas en las que el ganador
      empata con otro modelo dentro de `TOLERANCIA_EMPATE`;
    - `recuperacion_clase_*`: proporción de réplicas en las que la CLASE de
      equivalencia observacional del régimen verdadero está entre las ganadoras.
      Es la única recuperación exigible cuando dos familias predicen lo mismo.
    """
    if regimen not in REGIMENES_S002:
        raise ValueError(f"Régimen desconocido: {regimen!r}.")
    if n_replicas < 1:
        raise ValueError("n_replicas debe ser >= 1.")

    modelo_verdadero = MODELO_DE_REGIMEN[regimen]
    clase_verdadera = CLASE_OBSERVACIONAL[modelo_verdadero]
    seleccion_test: Dict[str, int] = {}
    seleccion_bic: Dict[str, int] = {}
    seleccion_bic_ef: Dict[str, int] = {}
    empates_test = empates_bic_ef = 0
    clase_test = clase_bic = clase_bic_ef = 0
    for i in range(n_replicas):
        data = generar_datos_regimen_s002(
            regimen,
            n_por_orden=n_por_orden,
            seed=seed + i,
            ruido=ruido,
        )
        train, test = dividir_train_test(
            data,
            proporcion_train=proporcion_train,
            seed=seed + 10000 + i,
        )
        resultados = evaluar_train_test_s002(train, test)
        ganador_test = seleccionar_modelo_s002(resultados, "test_log_likelihood")
        ganador_bic = seleccionar_modelo_s002(resultados, "train_BIC")
        ganador_bic_ef = seleccionar_modelo_s002(resultados, "train_BIC_efectivo")
        seleccion_test[ganador_test] = seleccion_test.get(ganador_test, 0) + 1
        seleccion_bic[ganador_bic] = seleccion_bic.get(ganador_bic, 0) + 1
        seleccion_bic_ef[ganador_bic_ef] = seleccion_bic_ef.get(ganador_bic_ef, 0) + 1

        empatados_test = modelos_empatados_s002(resultados, "test_log_likelihood")
        empatados_bic_ef = modelos_empatados_s002(resultados, "train_BIC_efectivo")
        empates_test += len(empatados_test) > 1
        empates_bic_ef += len(empatados_bic_ef) > 1
        clase_test += clase_verdadera in {CLASE_OBSERVACIONAL[m] for m in empatados_test}
        clase_bic += CLASE_OBSERVACIONAL[ganador_bic] == clase_verdadera
        clase_bic_ef += clase_verdadera in {CLASE_OBSERVACIONAL[m] for m in empatados_bic_ef}

    return {
        "regimen_verdadero": regimen,
        "modelo_verdadero": modelo_verdadero,
        "clase_observacional": clase_verdadera,
        "n_replicas": n_replicas,
        "frecuencia_test": seleccion_test,
        "frecuencia_bic": seleccion_bic,
        "frecuencia_bic_efectivo": seleccion_bic_ef,
        # Selección estricta del modelo generador. Antes se buscaba el nombre
        # del RÉGIMEN entre nombres de MODELOS, por lo que "sin_orden" (cuyo
        # modelo es "clasico_estatico") daba recuperación 0 por construcción.
        "recuperacion_test": seleccion_test.get(modelo_verdadero, 0) / n_replicas,
        "recuperacion_bic": seleccion_bic.get(modelo_verdadero, 0) / n_replicas,
        "recuperacion_bic_efectivo": seleccion_bic_ef.get(modelo_verdadero, 0) / n_replicas,
        "empates_test": int(empates_test),
        "empates_bic_efectivo": int(empates_bic_ef),
        "recuperacion_clase_test": clase_test / n_replicas,
        "recuperacion_clase_bic": clase_bic / n_replicas,
        "recuperacion_clase_bic_efectivo": clase_bic_ef / n_replicas,
    }


def matriz_recuperacion_s002(
    regimenes: Iterable[str] = REGIMENES_S002,
    n_replicas: int = 20,
    n_por_orden: int = 1000,
    seed: int = 2026,
    proporcion_train: float = 0.8,
    ruido: float = 0.05,
) -> Dict[str, Dict[str, object]]:
    """Construye la matriz de recuperación para todos los regímenes."""
    regimenes = tuple(regimenes)
    for regimen in regimenes:
        if regimen not in REGIMENES_S002:
            raise ValueError(f"Régimen desconocido: {regimen!r}.")
    return {
        regimen: evaluar_recuperacion_s002(
            regimen,
            n_replicas=n_replicas,
            n_por_orden=n_por_orden,
            seed=seed + i * 100000,
            proporcion_train=proporcion_train,
            ruido=ruido,
        )
        for i, regimen in enumerate(regimenes)
    }

def benchmark_s002(
    data: S002Dataset | None = None,
) -> Dict[str, Dict[str, float]]:
    """Ejecuta el benchmark con modelos controlados (parámetros FIJOS, sin ajustar).

    No es una comparación de familias: cada modelo usa valores por defecto
    arbitrarios y el dataset por defecto está generado cerca de la predicción
    quantum-like por defecto, que por eso obtiene el mejor ajuste. Sirve para
    comprobar que las métricas se calculan, no para concluir qué modelo es mejor.
    """
    data = data or generar_datos_s002()
    pred = {
        "clasico_estatico": baseline_clasico_estatico(),
        "clasico_secuencial": modelo_clasico_secuencial(),
        "vectorial_unitario": modelo_vectorial_unitario(),
        "quantum_like": modelo_quantum_like(),
    }
    return evaluar_predicciones(data, pred, N_PARAMS_NOMINALES)
