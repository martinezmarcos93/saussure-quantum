# 🚀 Guía de inicio rápido

**Saussure–Quantum Fusion** — para usuarios que quieren explorar el proyecto sin necesidad de saber programar.

---

## ¿Qué es este proyecto?

Es una herramienta que combina dos ideas que parecen muy distintas pero tienen una estructura matemática sorprendentemente parecida:

- **La lingüística de Ferdinand de Saussure** — que dice que las palabras no tienen significado por sí solas, sino por oponerse a otras palabras dentro de un sistema.
- **La mecánica cuántica** — que dice que los objetos físicos no tienen propiedades definidas hasta que son observados.

La tesis central es que **hablar es parecido a medir**: una palabra existe en "superposición" de significados posibles hasta que el contexto la colapsa a uno concreto.

---

## Instalación en 3 pasos

### Paso 1 — Instalar Python

Si no tenés Python instalado, descargalo desde [python.org](https://www.python.org/downloads/).  
Versión recomendada: **Python 3.10 o superior**.

### Paso 2 — Instalar el proyecto

Abrí una terminal (PowerShell en Windows, Terminal en Mac/Linux), navegá a la carpeta del proyecto y ejecutá:

```bash
pip install -r requirements.txt
pip install -e .
```

> ⚠️ El segundo comando (`pip install -e .`) es importante — sin él, el programa no puede encontrar sus propios módulos.

### Paso 3 — Abrir la interfaz gráfica

```bash
python gui.py
```

Se abrirá una ventana con todas las herramientas del proyecto.

---

## La interfaz gráfica

La GUI tiene un sidebar izquierdo con cinco secciones. Hacé clic en cualquiera para navegar:

```
◈  Poeta cuántico       → Genera poesía probabilística
◉  Simulador            → Demuestra el principio de incertidumbre
△  Incertidumbre        → Analizá tus propios conjuntos de palabras
⊗  Op. Diferencia       → Visualizá el "ser por no ser" de Saussure
❖  Teoría               → Conceptos y fundamentos explicados
```

---

## Las cinco herramientas

### ◈ Poeta cuántico

Genera versos usando colapsos probabilísticos. Cada palabra del poema comienza en superposición de todas las palabras posibles de su categoría y "colapsa" al ser elegida — igual que un electrón colapsa al ser medido.

**Cómo usarlo:**

1. Ajustá la cantidad de **versos** con el slider
2. Ajustá la **temperatura ℏ** — baja (1.0) genera versos más predecibles, alta (3.0) los hace más sorprendentes
3. Elegí el **modo**: Normal, Caótico o Mínima incertidumbre
4. Editá el **diccionario** con tus propias palabras (una por categoría, separadas por coma)
5. Hacé clic en **Generar poema**
6. Podés **Exportar .txt** para guardar el resultado con sus metadatos

**Tip:** probá cambiar los sustantivos por nombres de personas o lugares y los verbos por acciones cotidianas.

---

### ◉ Simulador de incertidumbre

Explora la **relación de incertidumbre de Robertson** entre el eje sintagmático y el paradigmático:

> ΔS·ΔP ≥ ½|⟨[S,P]⟩|

Es una analogía formal con posición-momento. En este modelo de dimensión finita la cota depende del estado y puede valer 0: un estado con sintagma exacto tiene ΔS = 0 y ΔP = ℏ/√2. No existe la cota universal ℏ/2.

**Cómo usarlo:**

1. Elegí el **tipo de estado** del menú desplegable
2. Ajustá la **dimensión** (tamaño del sistema lingüístico)
3. **Analizar estado** → muestra ΔS, ΔP y la cota de Robertson de ese estado
4. **Demostrar principio** → muestra tres estados de referencia con su cota
5. **Comparar 4 estados** → tabla que muestra los cuatro tipos juntos

**Qué significan los números:**
- `ΔS` = incertidumbre sintagmática (¿dónde está en la frase?)
- `ΔP` = incertidumbre paradigmática (¿con qué se puede reemplazar?)
- `ΔS·ΔP` = producto — nunca es menor que la cota de Robertson del propio estado (que puede ser 0)

---

### △ Principio de incertidumbre

Acá podés analizar **tus propios conjuntos de palabras**.

**Cómo usarlo:**

1. Escribí tus significantes separados por coma en el campo **Significantes**  
   Ejemplo: `perro, gato, ratón, pájaro`
2. Escribí las amplitudes en el campo **Amplitudes** (un número por significante)  
   Ejemplo: `1, 0.5, 0.3, 0.8`  
   No importa la escala — se normalizan automáticamente
3. O usá el menú **Cargar ejemplo** para cargar un conjunto predefinido
4. **Calcular incertidumbre** → análisis completo con barras de probabilidad
5. **Paradoja del observador** → muestra cómo medir un eje perturba el otro

**¿Qué son las amplitudes?**  
Representan qué tan "presente" está cada significante en el estado del signo. Una amplitud mayor = mayor probabilidad de que el signo colapse a ese valor. No tienen que sumar ningún valor en particular — el programa las normaliza.

**Ejemplos para probar:**
- Fonemas: `/p/, /b/, /t/` con amplitudes `1, 0.8, 0.6`
- Colores: `rojo, verde, azul` con amplitudes `1, 1, 1` (equiprobables)
- Conceptos: `verdad, mentira, duda, certeza` con amplitudes `1.5, 0.8, 0.5, 1.2`

---

### ⊗ Operador diferencia

Materializa la idea central de Saussure: **un signo ES porque NO ES los demás**.

> "En la lengua solo hay diferencias sin términos positivos." — Saussure, 1916

El Operador Diferencia D̂ transforma signos "sustanciales" (que parecen tener significado propio) en estados "diferenciales" (donde el significado emerge de las oposiciones).

**Cómo usarlo:**

1. Escribí los signos del sistema, **uno por línea**, en el cuadro de texto  
   Ejemplo:
   ```
   /p/
   /b/
   /t/
   ```
2. **Aplicar D̂** → muestra cómo cada signo se distribuye en el sistema
3. **Análisis de negatividad** → cuánto "debe" cada signo a no ser los otros
4. **Similitud diferencial** → qué tan parecidos son los signos entre sí
5. **Ver matriz D̂** → muestra la matriz matemática completa del operador

**Interpretación:**  
Después de aplicar D̂, el primer signo ya no tiene probabilidad 100% de colapsar a sí mismo — parte de su "ser" está distribuida en los otros signos del sistema. Eso es el "ser por no ser" de Saussure.

---

### ❖ Teoría

Panel de referencia con cinco subtemas navegables:

- **¿Qué es esto?** — introducción general al proyecto
- **Saussure** — conceptos de lingüística estructural
- **Mecánica cuántica** — principios relevantes de física cuántica
- **La fusión** — tabla de analogías y formalismo matemático
- **Herramientas** — descripción de cada panel

---

## Preguntas frecuentes

**¿Necesito saber física o lingüística para usar esto?**  
No. La GUI está diseñada para que puedas explorar las herramientas de forma intuitiva. El panel Teoría explica los conceptos a medida que los necesitás.

**¿Por qué el poema es diferente cada vez?**  
Porque cada palabra es elegida por un proceso probabilístico — como lanzar un dado cargado. El resultado nunca es completamente aleatorio ni completamente predecible.

**¿Por qué las amplitudes no tienen que sumar 1?**  
Porque el programa las normaliza automáticamente. Lo que importa es la proporción entre ellas: si ponés `2, 1` o `4, 2`, el resultado es el mismo.

**¿Puedo usar este proyecto para investigación académica?**  
Sí. Ver la sección de citación en el `README.md`.

**¿El programa funciona sin internet?**  
Sí, completamente offline. Solo necesitás Python y las dependencias instaladas.

---

## Estructura de archivos

```
saussure-quantum/
├── gui.py                  ← Ejecutar esto para abrir la interfaz
├── saussure_quantum/       ← El paquete Python (no modificar)
├── examples/               ← Scripts de ejemplo por línea de comandos
├── notebooks/              ← Jupyter notebooks educativos
├── docs/
│   ├── quickstart.md       ← Esta guía
│   └── referencia_api.md   ← Documentación técnica completa
└── README.md               ← Vista general del proyecto
```

---

## Ejecutar los ejemplos por línea de comandos

Si preferís usar el proyecto sin la GUI:

```bash
# Generador de poesía
python examples/generador_poetico_cuantico.py

# Simulador interactivo de incertidumbre
python examples/simulador_indeterminacion.py
```

---

## Soporte

- **Bugs y sugerencias:** abrí un Issue en GitHub
- **Preguntas conceptuales:** usá la sección Discussions
- **Email:** doomhammer793@gmail.com
