# 📚 Referencia de API — Saussure-Quantum Fusion

**Versión:** 0.1.0  
**Paquete:** `saussure_quantum`

---

## Índice

- [core.py — Clases base](#corepy--clases-base)
  - [SignoCuanto](#signocuanto)
  - [Langue](#langue)
- [operators.py — Operadores](#operatorspy--operadores)
  - [operador_diferencia()](#operador_diferencia)
  - [OperadorDiferencia](#operadordiferencia)
  - [similitud_diferencial()](#similitud_diferencial)
  - [principio_negatividad()](#principio_negatividad)
- [collapse.py — Colapso / Parole](#collapsepy--colapso--parole)
  - [colapso_parole()](#colapso_parole)
  - [ContextoEnunciativo](#contextoenunciativo)
  - [MedidorParole](#medidorparole)
  - [medicion_debil()](#medicion_debil)
  - [realidades_alternativas()](#realidades_alternativas)
- [uncertainty.py — Incertidumbre](#uncertaintypy--incertidumbre)
  - [ObservablesSaussureanos](#observablessaussureanos)
  - [PrincipioIncertidumbreSaussure](#principioincertidumbresaussure)
  - [incertidumbre_saussure_heisenberg()](#incertidumbre_saussure_heisenberg)
  - [paradoja_del_observador_linguistico()](#paradoja_del_observador_linguistico)

---

## `core.py` — Clases base

### `SignoCuanto`

Representa un signo lingüístico como un estado cuántico en superposición.

```python
from saussure_quantum import SignoCuanto

signo = SignoCuanto(
    significantes=["sol", "luna", "estrella"],
    amplitudes=[1, 0.5j, 0.7]
)
```

#### Constructor

```python
SignoCuanto(significantes: List[str], amplitudes: Optional[List[complex]] = None)
```

| Parámetro | Tipo | Descripción |
|---|---|---|
| `significantes` | `List[str]` | Etiquetas de los posibles valores del signo |
| `amplitudes` | `List[complex]` \| `None` | Amplitudes complejas. Si es `None`, se genera superposición equitativa |

Las amplitudes se normalizan automáticamente al construir el objeto.

#### Atributos

| Atributo | Tipo | Descripción |
|---|---|---|
| `significantes` | `List[str]` | Lista de etiquetas |
| `amplitudes` | `np.ndarray` (complex) | Vector de amplitudes normalizado |
| `dimension` | `int` | Dimensión del espacio (cantidad de significantes) |

#### Métodos

**`normalizar() → None`**  
Normaliza el vector de amplitudes a norma L2 = 1.

**`probabilidad(significante: str | int) → float`**  
Retorna la probabilidad de colapso a un significante dado (`|αᵢ|²`).

```python
signo.probabilidad("sol")    # por nombre
signo.probabilidad(0)        # por índice
```

**`colapsar(idx: int | None) → (str, SignoCuanto)`**  
Colapsa la superposición. Retorna una tupla `(significante, estado_colapsado)`.  
No muta el objeto original.

```python
sig, nuevo_estado = signo.colapsar()
sig, nuevo_estado = signo.colapsar(idx=0)  # forzar resultado
```

> ⚠️ **Cambio de firma:** versiones anteriores retornaban solo `str` y mutaban `self`. La firma actual es inmutable y retorna tupla.

**`densidad() → np.ndarray`**  
Retorna la matriz densidad `ρ = |ψ⟩⟨ψ|` de dimensión `d×d`.

**`fase_relativa(i: int, j: int) → float`**  
Retorna el ángulo de fase relativa entre dos componentes en radianes.

---

### `Langue`

Sistema de la lengua como espacio de Hilbert. Define el vocabulario y los operaciones sobre él.

```python
from saussure_quantum import Langue

# Língua genérica
lang = Langue(10)

# Langue con términos personalizados
lang = Langue(3, terminos=["/p/", "/b/", "/t/"])
```

#### Constructor

```python
Langue(dimension: int, nombre: str = "Langue", terminos: Optional[List[str]] = None)
```

| Parámetro | Tipo | Descripción |
|---|---|---|
| `dimension` | `int` | Dimensión del espacio de Hilbert |
| `nombre` | `str` | Identificador del sistema |
| `terminos` | `List[str]` \| `None` | Etiquetas personalizadas. Debe tener exactamente `dimension` elementos si se provee |

#### Métodos

**`estado_base(idx: int) → SignoCuanto`**  
Retorna el estado base `|idx⟩` — signo colapsado al término `idx`.

**`superposicion(coeficientes: List[complex]) → SignoCuanto`**  
Crea un estado en superposición con los coeficientes dados.

**`base_canonica() → List[SignoCuanto]`**  
Retorna todos los estados base del espacio.

**`producto_interno(psi: SignoCuanto, phi: SignoCuanto) → complex`**  
Calcula `⟨ψ|φ⟩`. Representa similitud semántica cuántica.

---

## `operators.py` — Operadores

### `operador_diferencia()`

Aplica el principio de diferencia pura de Saussure a un conjunto de estados.

```python
from saussure_quantum.operators import operador_diferencia

fonema_p = SignoCuanto(["/p/", "/b/", "/t/"], [1, 0, 0])
fonema_b = SignoCuanto(["/p/", "/b/", "/t/"], [0, 1, 0])
fonema_t = SignoCuanto(["/p/", "/b/", "/t/"], [0, 0, 1])

diferencia = operador_diferencia([fonema_p, fonema_b, fonema_t])
```

```python
operador_diferencia(estados: List[SignoCuanto], normalizar: bool = True) → SignoCuanto
```

| Parámetro | Tipo | Descripción |
|---|---|---|
| `estados` | `List[SignoCuanto]` | Al menos 2 estados. Deben tener la misma dimensión **y los mismos significantes** |
| `normalizar` | `bool` | Si normalizar el resultado (default: `True`) |

**Fórmula:**  
`D̂(|ψ₁⟩, ..., |ψₙ⟩) = Σᵢ﹤ⱼ (|ψᵢ⟩ − |ψⱼ⟩)`

> ⚠️ Lanza `ValueError` si los significantes de los estados no coinciden exactamente.

---

### `OperadorDiferencia`

Versión orientada a objetos del operador diferencia. Permite aplicarlo múltiples veces sobre distintos estados.

```python
from saussure_quantum.operators import OperadorDiferencia

lang = Langue(4, terminos=["a", "b", "c", "d"])
op = OperadorDiferencia(lang)
```

#### Métodos

**`aplicar(estado: SignoCuanto) → SignoCuanto`**  
Aplica `D̂|ψ⟩` y retorna el nuevo estado.

**`valor_esperado(estado: SignoCuanto) → float`**  
Calcula `⟨ψ|D̂|ψ⟩`. Mayor valor = más diferenciado del sistema base.

**`medir_diferencia(estado: SignoCuanto) → (float, SignoCuanto)`**  
Mide el observable diferencia, colapsando el estado a un autovector.  
Retorna `(valor_medido, estado_colapsado)`.

**`matriz() → np.ndarray`**  
Retorna la matriz `D = d·I − J` donde `J` es la matriz de unos.

---

### `similitud_diferencial()`

Calcula el solapamiento `|⟨ψ|φ⟩|` entre dos signos. Pese al nombre, no usa el operador diferencia.

```python
from saussure_quantum.operators import similitud_diferencial

sim = similitud_diferencial(estado1, estado2)
# Retorna float en [0, 1]
# 1.0 = idénticos, 0.0 = ortogonales
```

```python
similitud_diferencial(estado1: SignoCuanto, estado2: SignoCuanto) → float
```

---

### `principio_negatividad()`

Analiza cuánto "debe" cada significante a no ser los otros.

```python
from saussure_quantum.operators import principio_negatividad

resultado = principio_negatividad(diferencia)
print(resultado["negatividad_total"])
print(resultado["significante_principal"])
print(resultado["negatividad_por_significante"])
```

**Retorna** un `dict` con:

| Clave | Tipo | Descripción |
|---|---|---|
| `significante_principal` | `str` | El de mayor amplitud |
| `negatividad_por_significante` | `Dict[str, float]` | Fuerza negativa de cada signo |
| `negatividad_total` | `float` | Suma total. Vale siempre `d − 1`: es constante para una dimensión dada |
| `estado` | `SignoCuanto` | El estado analizado |

---

## `collapse.py` — Colapso / Parole

### `colapso_parole()`

Función principal de colapso. Modela el acto de habla como medición cuántica.

```python
from saussure_quantum.collapse import colapso_parole, ContextoEnunciativo

signo = SignoCuanto(["sol", "luna"], [1, 0.5])
resultado, estado_colapsado, info = colapso_parole(signo)
```

```python
colapso_parole(
    estado: SignoCuanto,
    contexto: Optional[ContextoEnunciativo] = None,
    indice_forzado: Optional[int] = None,
    seed: Optional[int] = None
) → Tuple[str, SignoCuanto, Dict]
```

**Retorna** una tupla `(significante, estado_colapsado, info)` donde `info` contiene:

| Clave | Descripción |
|---|---|
| `probabilidades_originales` | `List[float]` con `|αᵢ|²` originales |
| `probabilidades_modificadas` | Después de aplicar el contexto |
| `indice_seleccionado` | Índice del resultado |
| `incertidumbre_medicion` | Entropía de Shannon de la distribución usada |

---

### `ContextoEnunciativo`

Modela el contexto del acto de habla (análogo al aparato de medición cuántico).

```python
from saussure_quantum.collapse import ContextoEnunciativo

ctx = ContextoEnunciativo(
    temperatura_semantica=1.5,
    intencionalidad=[0.7, 0.2, 0.1],
    ruido_ambiental=0.05
)
```

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `temperatura_semantica` | `float` | `1.0` | `< 1` concentra en lo más probable, `> 1` distribuye más uniformemente |
| `intencionalidad` | `List[float]` \| `None` | `None` | Sesgo hacia ciertos significantes (se normaliza automáticamente) |
| `ruido_ambiental` | `float` | `0.0` | Probabilidad de error en la medición |

---

### `MedidorParole`

Permite realizar múltiples mediciones manteniendo historial y estadísticas.

```python
from saussure_quantum.collapse import MedidorParole

medidor = MedidorParole()
sig, estado = medidor.medir(signo)

frecuencias = medidor.medir_multiples(signo, n_mediciones=1000)
print(medidor.entropia_parole())
medidor.reset()
```

---

### `medicion_debil()`

Simula un colapso gradual con una contracción heurística repetida. No implementa una medición débil canónica (POVM/Kraus). Acepta `seed` para reproducir el colapso final; `fuerza` debe estar en `[0, 1]`.

```python
from saussure_quantum.collapse import medicion_debil

resultado, estado_final, registro = medicion_debil(
    estado, fuerza=0.3, n_pasos=5
)
```

```python
medicion_debil(
    estado: SignoCuanto,
    fuerza: float = 0.3,
    n_pasos: int = 5
) → Tuple[str, SignoCuanto, List[Dict]]
```

| Parámetro | Descripción |
|---|---|
| `fuerza` | `0` = sin efecto, `1` = colapso inmediato |
| `n_pasos` | Pasos antes del colapso final |

Cada paso aplica `peso_i = (1 - fuerza) + fuerza * prob_i`, reduciendo gradualmente la entropía.

---

### `realidades_alternativas()`

Genera múltiples realizaciones del mismo estado inicial.

```python
from saussure_quantum.collapse import realidades_alternativas

realidades = realidades_alternativas(signo, n_realidades=10)
```

---

## `uncertainty.py` — Incertidumbre

### `ObservablesSaussureanos`

Implementa los observables complementarios Ŝ (sintagma) y P̂ (paradigma).

```python
from saussure_quantum.uncertainty import ObservablesSaussureanos

obs = ObservablesSaussureanos(dimension=20, hbar=1.0)
delta_S, delta_P, producto = obs.incertidumbre(estado)
```

#### Constructor

```python
ObservablesSaussureanos(dimension: int, hbar: float = 1.0)
```

#### Atributos

| Atributo | Descripción |
|---|---|
| `S` | Matriz del operador sintagma (diagonal con `0,...,d-1`) |
| `P` | Matriz del operador paradigma (diferencias finitas periódicas) |
| `dimension` | Dimensión del espacio |
| `hbar` | Constante de Planck semiótica |

#### Métodos

**`incertidumbre(estado: SignoCuanto) → (float, float, float)`**  
Retorna `(ΔS, ΔP, ΔS·ΔP)`.

**`verificar_conmutacion(tolerancia: float = 1e-10) → bool`**  
Verifica si `[S, P] ≈ iℏI`. Siempre retorna `False` en dimensión finita (limitación matemática — ver nota).

**`error_conmutacion() → float`**  
Retorna `‖[S,P] − iℏI‖` (norma de Frobenius). Más útil que `verificar_conmutacion()` para diagnóstico.

**`estado_minima_incertidumbre() → SignoCuanto`**  
Genera un estado gaussiano de referencia. El nombre es histórico: no minimiza `ΔS·ΔP` (los estados base y las ondas planas tienen producto 0) ni se afirma que sature Robertson.

> 📐 **Nota matemática:** La relación `[Ŝ, P̂] = iℏI` es imposible en dimensión finita porque `Tr([S,P]) = 0` pero `Tr(iℏI) = iℏd ≠ 0`. El operador P usa condiciones de borde periódicas que minimizan el error de borde frente al operador tridiagonal abierto.

---

### `PrincipioIncertidumbreSaussure`

Analiza la incertidumbre de estados en el contexto de una `Langue` específica.

```python
from saussure_quantum import Langue
from saussure_quantum.uncertainty import PrincipioIncertidumbreSaussure

lang = Langue(10)
principio = PrincipioIncertidumbreSaussure(lang)

estado = principio.estado_sintagmatico_puro(3)
analisis = principio.analizar_estado(estado)
```

#### Métodos

**`analizar_estado(estado: SignoCuanto) → Dict`**  
Análisis completo. Retorna un `dict` con:

| Clave | Tipo | Descripción |
|---|---|---|
| `delta_sintagma` | `float` | ΔS |
| `delta_paradigma` | `float` | ΔP |
| `producto_incertidumbre` | `float` | ΔS·ΔP |
| `cota_robertson` | `float` | ½\|⟨[S,P]⟩\|, calculada para ese estado |
| `valor_conmutador` | `complex` | ⟨[S,P]⟩ |
| `satisface_robertson` | `bool` | ΔS·ΔP ≥ ½\|⟨[S,P]⟩\| |
| `factor_sobre_cota` | `float` | ΔS·ΔP / cota de Robertson (`inf` si la cota es 0) |
| `interpretacion` | `str` | Descripción cualitativa |
| `dominancia` | `str` | Qué eje predomina |

**`estado_sintagmatico_puro(posicion: int) → SignoCuanto`**  
Estado con posición sintagmática perfectamente definida (ΔS = 0).

**`estado_paradigmatico_puro(momento: int) → SignoCuanto`**  
Estado con modo paradigmático perfectamente definido (onda plana, ΔP = 0).

**`estado_maxima_incertidumbre() → SignoCuanto`**  
Superposición uniforme. Nombre histórico: es la onda plana de modo 0, con ΔP = 0 y producto 0.

**`demostrar_principio() → Dict`**  
Calcula tres estados de referencia (sintagmático puro, paradigmático puro, gaussiano), cada uno con `producto` y `cota_robertson`.

**`visualizar_espacio_fase(estado: SignoCuanto) → np.ndarray`**  
Retorna la función de Wigner discreta `W[x,p]` (suma 1; marginal en x exacta; marginal en p exacta sólo para dimensión impar).

---

### `incertidumbre_saussure_heisenberg()`

Función de alto nivel para calcular la incertidumbre de cualquier signo.

```python
from saussure_quantum.uncertainty import incertidumbre_saussure_heisenberg

signo = SignoCuanto(["amor", "odio", "duda"], [1, 0.5, 0.3])
resultado = incertidumbre_saussure_heisenberg(signo)
print(resultado["producto_incertidumbre"])
```

```python
incertidumbre_saussure_heisenberg(
    estado: SignoCuanto,
    hbar: float = 1.0
) → Dict
```

Internamente crea una `Langue` temporal de la dimensión del estado y delega a `PrincipioIncertidumbreSaussure.analizar_estado()`.

---

### `paradoja_del_observador_linguistico()`

Compara las dispersiones antes y después de proyectar sobre el autovector más probable de cada eje. La perturbación depende del estado.

```python
from saussure_quantum.uncertainty import paradoja_del_observador_linguistico

resultado = paradoja_del_observador_linguistico(estado)
```

**Retorna** un `dict` con tres secciones:

```python
{
    "estado_original": {"delta_S", "delta_P", "producto"},
    "despues_medir_sintagma": {"delta_S", "delta_P", "producto", "cambio_significativo"},
    "despues_medir_paradigma": {"delta_S", "delta_P", "producto", "cambio_significativo"},
    "perturbacion_observada": bool   # calculado; antes era una constante True
}
```

`cambio_significativo` es `True` si la perturbación supera 1.5× el valor original.

---

## Constantes

| Constante | Módulo | Valor | Descripción |
|---|---|---|---|
| `HBAR_SEMIOTICO` | `uncertainty` | `1.0` | Constante de Planck semiótica |

## Alias

| Alias | Función original | Módulo |
|---|---|---|
| `habla` | `colapso_parole` | `collapse` |
| `acto_de_significacion` | `colapso_parole` | `collapse` |
| `emergencia_de_realidad` | `colapso_parole` | `collapse` |
| `incertidumbre_linguistica` | `incertidumbre_saussure_heisenberg` | `uncertainty` |
| `principio_saussure_heisenberg` | `incertidumbre_saussure_heisenberg` | `uncertainty` |
| `D_hat` | `operador_diferencia` | `operators` |
| `D_matrix` | `operador_diferencia_matriz` | `operators` |
