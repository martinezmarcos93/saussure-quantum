# 🌌 Saussure–Quantum Fusion 🧠⚛️

**Una implementación computacional de la fusión entre la semiótica estructural de Ferdinand de Saussure y la mecánica cuántica.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://pytest.org)

---

## 📖 ¿De qué trata esto?

Este repositorio materializa computacionalmente la tesis del informe *"Hacia una Fusión de la Semiótica Saussureana y la Mecánica Cuántica"*, que propone analogías formales entre ambos sistemas (no equivalencias físicas ni resultados empíricos sobre el lenguaje):

| Concepto Saussureano | Análogo Cuántico | Implementación |
|---|---|---|
| Signo lingüístico | Estado cuántico | `SignoCuanto` |
| Valor diferencial (negatividad) | Amplitud de probabilidad | `operador_diferencia()` |
| Lengua (*langue*) | Espacio de Hilbert | `Langue` |
| Habla (*parole*) | Colapso por medición | `colapso_parole()` |
| Eje paradigmático | Momento (P̂) | `ObservablesSaussureanos.P` |
| Eje sintagmático | Posición (Ŝ) | `ObservablesSaussureanos.S` |
| Indeterminación semántica | Relación de incertidumbre de Robertson | `incertidumbre_saussure_heisenberg()` |

> **Alcance.** La columna "análogo cuántico" nombra una correspondencia de modelado. El paquete valida propiedades matemáticas del formalismo; no demuestra que el significado sea físicamente cuántico. El estado de cada afirmación (validada, parcial, no validada) está en [`docs/RESULTADOS_VALIDACION_LOCAL.md`](docs/RESULTADOS_VALIDACION_LOCAL.md).

### 🎯 Tesis central

> **La realidad no es una sustancia, sino un efecto de segundo orden que emerge de la diferencia observada.**

El mundo no está hecho de objetos, sino de relaciones de oposición. Una "silla" no es tal por su esencia, sino por oponerse a "mesa", "sillón", "banco" (Saussure) y, además, su existencia macroscópica estable es el resultado de un colapso cuántico previo (Bohr).

---

## ✨ Características

- ✅ **Signo-cuanto**: Representación de signos como estados en superposición con amplitudes complejas
- ✅ **Operador diferencia (D̂)**: Implementa el principio saussureano de negatividad esencial
- ✅ **Colapso semiótico**: Simula el acto de *parole* como medición cuántica
- ✅ **Contextos enunciativos**: Sesgos, temperatura semántica y ruido ambiental
- ✅ **Relación de incertidumbre**: cota de Robertson entre los ejes paradigmático y sintagmático (depende del estado; no hay cota universal ℏ/2 en dimensión finita)
- ✅ **Colapso gradual heurístico** (`medicion_debil`): no es una medición débil canónica POVM/Kraus
- ✅ **Realidades alternativas**: Múltiples emergencias desde el mismo estado inicial
- ✅ **Poeta cuántico**: Aplicación creativa que genera poesía por colapso cuántico
- ✅ **Interfaz gráfica (GUI)**: Acceso visual a todas las herramientas sin línea de comandos

---

## 🚀 Instalación rápida

```bash
# Clonar repositorio
git clone https://github.com/martinezmarcos93/saussure-quantum.git
cd saussure-quantum

# Instalar dependencias
pip install -r requirements.txt

# Instalar el paquete en modo desarrollo (necesario para los imports)
pip install -e .

# Ejecutar la interfaz gráfica
python gui.py
```

> ⚠️ **Importante:** el paso `pip install -e .` es necesario para que todos los módulos
> puedan importar `saussure_quantum` correctamente, tanto desde la raíz como desde
> las carpetas `examples/` y `tests/`.

### Dependencias mínimas

```
numpy>=1.21.0      # Álgebra lineal cuántica
scipy>=1.7.0       # Operaciones avanzadas
matplotlib>=3.4.0  # Visualizaciones
```

### Dependencias opcionales

```bash
# Para herramientas de desarrollo (tests, linting)
pip install -e ".[dev]"

# Para integración futura con hardware cuántico real
pip install -e ".[quantum]"
```

---

## 🖥️ Interfaz gráfica

La forma más sencilla de explorar el proyecto es a través de la GUI:

```bash
python gui.py
```

La interfaz incluye cuatro paneles navegables desde el sidebar:

| Panel | Descripción |
|---|---|
| **◈ Poeta cuántico** | Genera versos por colapso de superposiciones semánticas. Sliders para número de versos, temperatura ℏ y modo (normal / caótico / mínima incertidumbre). Muestra métricas de palabras, colapsos y entropía media. |
| **◉ Simulador** | Explora la cota de Robertson ΔS·ΔP ≥ ½\|⟨[S,P]⟩\|. Elegís el tipo de estado (sintagmático puro, paradigmático puro, mínima incertidumbre, uniforme), la dimensión y la posición, y analizás o demostrás el principio completo. |
| **△ Incertidumbre** | Ingresás tus propios significantes y amplitudes, calculás la incertidumbre con barras de probabilidad, o ejecutás la paradoja del observador para ver cómo medir un eje perturba el otro. |
| **⊗ Op. Diferencia** | Ingresás signos línea por línea, aplicás D̂, analizás la negatividad de cada signo, o calculás la similitud diferencial entre todos los pares del sistema. |

---

## 📓 Primeros pasos (uso programático)

### Ejemplo 1: Crear un signo-cuanto

```python
from saussure_quantum import SignoCuanto

# Un signo en superposición de tres significados
signo = SignoCuanto(
    significantes=["🌞 sol", "🌙 luna", "⭐ estrella"],
    amplitudes=[1, 0.5j, 0.7]
)

print(signo)
# Signo-cuanto (d=3):
#   🌞 sol:     |0.816|² = 66.6%
#   🌙 luna:    |0.408|² = 16.7%
#   ⭐ estrella: |0.408|² = 16.7%
```

### Ejemplo 2: El acto de parole (colapso)

```python
from saussure_quantum.collapse import colapso_parole

# El hablante "dice" la palabra → la realidad emerge
realidad, estado_colapsado, info = colapso_parole(signo)
print(f"El hablante dijo: {realidad}")
# Salida posible: "El hablante dijo: 🌞 sol"
```

### Ejemplo 3: Principio de negatividad (Saussure puro)

```python
from saussure_quantum.operators import operador_diferencia

# Tres fonemas puros
fonema_p = SignoCuanto(["/p/", "/b/", "/t/"], [1, 0, 0])
fonema_b = SignoCuanto(["/p/", "/b/", "/t/"], [0, 1, 0])
fonema_t = SignoCuanto(["/p/", "/b/", "/t/"], [0, 0, 1])

# Aplicar el operador diferencia
diferencia_pura = operador_diferencia([fonema_p, fonema_b, fonema_t])
print(diferencia_pura)
# Σ_{i<j}(ψᵢ − ψⱼ) = 2·/p/ − 2·/t/: con tres estados el del medio (/b/) recibe
# coeficiente 0 y el resultado depende del orden de la lista.
```

> `operador_diferencia` (suma por pares de varios estados) y `OperadorDiferencia` (la matriz `D = d·I − J`, que actúa sobre un solo estado) son construcciones distintas y no equivalentes.

### Ejemplo 4: Principio de incertidumbre Saussure-Heisenberg

```python
from saussure_quantum import Langue
from saussure_quantum.uncertainty import incertidumbre_saussure_heisenberg

# Crear un sistema lengua con términos personalizados
lang = Langue(10, terminos=["the","a","of","in","to","and","is","was","he","she"])

# Estado con posición sintagmática bien definida
estado = lang.estado_base(0)

analisis = incertidumbre_saussure_heisenberg(estado)
print(f"ΔS (sintagma):  {analisis['delta_sintagma']:.3f}")
print(f"ΔP (paradigma): {analisis['delta_paradigma']:.3f}")
print(f"ΔS·ΔP = {analisis['producto_incertidumbre']:.3f} ≥ cota de Robertson = {analisis['cota_robertson']:.3f}")
# ΔS = 0.000, ΔP = 0.707 (= ℏ/√2), producto 0.000 ≥ 0.000.
# Un estado base tiene producto 0: la cota canónica ℏ/2 NO vale en dimensión finita.
```

---

## 🎨 Aplicaciones incluidas

### Poeta Cuántico (línea de comandos)

```bash
python examples/generador_poetico_cuantico.py
```

Ejemplo de salida:

```
POEMA 1: HUMOR NORMAL
Amor nace eterno
Profundo caos vuela
Sueña luz fugaz
Cuando el infinito asciende
```

### Simulador de incertidumbre (línea de comandos)

```bash
python examples/simulador_indeterminacion.py
```

---

## 🧪 Ejecutar pruebas

```bash
# Todas las pruebas
pytest tests/ -v

# Solo pruebas de core
pytest tests/test_core.py -v

# Solo pruebas de incertidumbre
pytest tests/test_uncertainty.py -v

# Con cobertura
pytest tests/ --cov=saussure_quantum --cov-report=html
```

---

## 📐 Arquitectura conceptual

```
Langue (Espacio de Hilbert)
    │
    ├── Estados base (términos lingüísticos puros)
    │
    └── Superposiciones (signos-cuanto)
         │
         └── Parole = Medición (colapso)
              │
              └── Realidad emergente
```

**Formalismo matemático:**

```
|signo⟩ = Σᵢ αᵢ |sᵢ⟩      donde αᵢ ∈ ℂ

|realidad⟩ = M̂_parole |lengua⟩

D̂(ψ₁…ψₙ) = Σᵢ﹤ⱼ (|ψᵢ⟩ − |ψⱼ⟩)   (diferencia por pares; depende del orden)
D = d·I − J = d·(I − |u⟩⟨u|)       (operador matricial; laplaciano de K_d)

[Ŝ, P̂] ≠ iℏI                       (la relación canónica es imposible en dim. finita)

ΔS · ΔP ≥ ½ |⟨[Ŝ, P̂]⟩|            (Robertson; la cota depende del estado y puede ser 0)
```

> **Nota matemática:** La relación `[Ŝ, P̂] = iℏI` es imposible en dimensión finita
> (Tr([S,P]) = 0 pero Tr(iℏI) = iℏd ≠ 0). El operador P̂ usa condiciones de borde
> periódicas que minimizan el error de borde. Ver `error_conmutacion()` para diagnóstico.
> Por eso tampoco existe la cota universal `ΔS·ΔP ≥ ℏ/2`: un estado base tiene `ΔS = 0`,
> `ΔP = ℏ/√2` y producto 0. P̂ requiere dimensión ≥ 3 (en 1 y 2 es idénticamente nulo).

---

## 📁 Estructura del proyecto

```
saussure-quantum/
│
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── gui.py                          ← Interfaz gráfica (entrada principal)
│
├── saussure_quantum/               ← Paquete Python
│   ├── __init__.py
│   ├── core.py                     ← SignoCuanto, Langue
│   ├── operators.py                ← OperadorDiferencia, similitud_diferencial
│   ├── collapse.py                 ← colapso_parole, medicion_debil
│   └── uncertainty.py              ← PrincipioIncertidumbreSaussure
│
├── notebooks/
│   ├── 01_intro_signo_cuanto.ipynb
│   ├── 02_operador_diferencia.ipynb
│   ├── 03_lengua_como_espacio_hilbert.ipynb
│   ├── 04_principio_incertidumbre_saussure_heisenberg.ipynb
│   └── 05_colapso_semantico_demo.ipynb
│
├── examples/
│   ├── generador_poetico_cuantico.py
│   └── simulador_indeterminacion.py
│
├── tests/
│   ├── test_core.py
│   └── test_uncertainty.py
│
└── docs/
    └── teoria_fusion.pdf
```

---

## 🔬 Comparación con otros modelos

| Modelo | Enfoque | Diferencia con este proyecto |
|---|---|---|
| Word2Vec / GloVe | Embeddings clásicos | No incorporan superposición ni colapso |
| BERT / GPT | Contexto determinista | Un solo significado por token, no probabilidad cuántica |
| Quantum NLP (QNLP) | Circuitos cuánticos reales | Nuestro foco es la analogía estructural, no hardware |
| Teoría de prototipos (Rosch) | Grados de membresía | No tiene formalismo de amplitudes complejas |

---

## 🗺️ Roadmap

- [x] Implementación base (vectores, colapso)
- [x] Operador diferencia D̂
- [x] Principio de incertidumbre Saussure-Heisenberg
- [x] Pruebas unitarias
- [x] Poeta cuántico (aplicación demo)
- [x] Interfaz gráfica con todas las herramientas (GUI Tkinter)
- [x] Langue con términos personalizados
- [x] Colapso gradual heurístico (no es medición débil POVM/Kraus)
- [x] Benchmark S002 con ajuste train/test y recuperación de modelo generador (resultado: el diseño binario de dos órdenes no distingue quantum-like del baseline clásico)
- [ ] Entrelazamiento semántico (correlaciones no locales)
- [ ] Integración con Qiskit (hardware cuántico real)
- [ ] Notebooks interactivos completos
- [ ] Visualizaciones 3D del espacio de Hilbert lingüístico
- [ ] Publicación académica

---

## 📚 Fundamentos teóricos

### Saussure (1916)

> "En la lengua solo hay diferencias sin términos positivos"

- El valor lingüístico es puramente diferencial y negativo
- La lengua es un sistema de oposiciones
- No hay conceptos preexistentes, solo valores emergentes

### Mecánica Cuántica (Bohr, Heisenberg, 1920s)

> "No hay fenómeno cuántico sin observación"

- Los estados son superposiciones hasta ser medidos
- Propiedades complementarias (posición/momento)
- El observador es constitutivo de la realidad

### Fusión (Este proyecto)

> "La realidad emerge del acoplamiento de dos sistemas diferenciales: el lenguaje y el cuanto"

---

## 🤝 Cómo contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-idea`)
3. Commit tus cambios (`git commit -m 'Add amazing idea'`)
4. Push a la rama (`git push origin feature/amazing-idea`)
5. Abre un Pull Request

**Áreas de contribución bienvenidas:**
- Implementación del entrelazamiento semántico
- Visualizaciones del espacio de Hilbert lingüístico
- Optimizaciones numéricas
- Nuevas aplicaciones (chatbot cuántico, traductor, etc.)
- Notebooks educativos

---

## 📄 Licencia

MIT © Marcos Martínez — Ver archivo [LICENSE](LICENSE)

---

## 📖 Citación

Si usas este trabajo en investigación académica:

```bibtex
@software{martinez_2026_saussure_quantum,
  author = {Martínez, Marcos},
  title  = {Saussure-Quantum Fusion: A Computational Implementation},
  year   = {2026},
  url    = {https://github.com/martinezmarcos93/saussure-quantum}
}
```

---

## 💬 Contacto y discusión

- **Issues**: Bugs y sugerencias específicas
- **Discussions**: Conversaciones conceptuales y preguntas
- **Email**: doomhammer793@gmail.com

---

## 🎭 Cierre conceptual

```
┌─────────────────────────────────────────────────────────────┐
│                    REALIDAD EPISTÉMICA                       │
│                                                              │
│   ┌──────────────┐         ┌──────────────┐                │
│   │   LANGUE     │ ──────→ │    PAROLE    │                │
│   │ (Potencial)  │ Medición │  (Realidad)  │                │
│   └──────────────┘         └──────────────┘                │
│          ↑                          ↓                       │
│    Superposición               Colapso                      │
│    de significados             a un significado             │
│                                                              │
│   "El ser es un efecto de la diferencia observada"          │
└─────────────────────────────────────────────────────────────┘
```

> "No hay una realidad en sí. Hay realidades epistémicas producidas por el acoplamiento
> de dos sistemas diferenciales: el lenguaje y el cuanto. El ser es un efecto de la
> diferencia observada."
>
> — *Fusión Saussure–Cuántica, 2026*

---

⭐ Si este proyecto te parece interesante, ¡deja una estrella en GitHub!
