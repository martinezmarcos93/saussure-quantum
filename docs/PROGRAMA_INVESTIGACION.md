# Saussure-Quantum — Programa de investigación

## Rol del proyecto

Saussure-Quantum es el componente semiótico del programa: estudiar el significado como un estado dependiente del contexto y explorar si representaciones quantum-like ofrecen ventajas sobre modelos clásicos.

## Hipótesis central

Un signo no tiene por qué tratarse computacionalmente como una variable fija. Puede modelarse como un estado cuya distribución de interpretaciones cambia al interactuar con contexto, otros signos y observación.

## Modelo mínimo

Para un concepto con dos alternativas:

    |ψ⟩ = α|0⟩ + β|1⟩

Para espacios de mayor dimensión:

    |ψ⟩ = Σᵢ αᵢ|i⟩

con:

    Σᵢ |αᵢ|² = 1

Una medición contextual define una distribución de resultados.

## Comparación obligatoria

Cada experimento deberá comparar:

- baseline clásico;
- modelo probabilístico/vectorial;
- modelo quantum-like.

No se debe asumir superioridad del último.

## Experimentos iniciales

### S001 — Estado semántico contextual

Usar un término polisémico y varios contextos. Medir cómo cambia la distribución de interpretaciones.

Ejemplo:

    AGUA
    ├── mar
    ├── bautismo
    ├── nacimiento
    └── contaminación

### S002 — Efecto de orden (cerrado: benchmark de identificabilidad)

Presentar pares de preguntas/estímulos en órdenes A→B y B→A y comparar la distribución de la respuesta final.

Resultado metodológico negativo: con una respuesta binaria y dos órdenes el modelo clásico secuencial es saturado y el quantum-like no es distinguible del vectorial. Se conserva como benchmark de identificabilidad. Ver `docs/EXPERIMENTOS/S002_EFECTO_ORDEN.md`.

### S003 — Respuestas conjuntas e igualdad QQ (cerrado en su fase sintética)

Registrar las dos respuestas de cada orden y contrastar la igualdad QQ de Wang y Busemeyer.

Resultado: la igualdad es una predicción falsable del modelo proyectivo, pero no discrimina "clásico frente a cuántico". Ver `docs/EXPERIMENTOS/S003_IGUALDAD_QQ.md` y `docs/RESULTADOS_S003.md`.

### Experimentos posteriores (no iniciados)

El orden y el contenido de los siguientes dependen de lo que S003 dejó establecido; ninguno debe empezar sin un análisis previo de identificabilidad.

- **Interferencia semántica**: determinar si una combinación contextual genera distribuciones que no se ajustan a una mezcla clásica.
- **Composición**: representar dos conceptos y estudiar el estado resultante de su combinación.
- **Contextualidad**: determinar si un mismo signo requiere estados distintos para contextos distintos y si esa dependencia mejora la predicción.

## Puente con el Laboratorio Cuántico-Junguiano

La salida de este proyecto puede convertirse en entrada del laboratorio psicológico:

    signo
      ↓
    significado contextual
      ↓
    estado semántico
      ↓
    activación simbólica
      ↓
    estado psicológico

## Requisitos científicos

Todo resultado debe incluir:
- datos;
- modelo;
- parámetros;
- métrica;
- baseline;
- predicción;
- incertidumbre;
- reproducibilidad;
- limitaciones.

## Posición epistemológica

El proyecto estudia modelos matemáticos inspirados en teoría cuántica. No afirma que el significado sea físicamente cuántico.

## Estado

| Etapa | Estado | Resultado |
|---|---|---|
| Auditoría de la implementación | Hecha | `docs/RESULTADOS_VALIDACION_LOCAL.md` |
| S001 | Cerrado | El modelo diagonal es idéntico al baseline clásico |
| S002 | Cerrado | Resultado negativo de diseño: no identificable |
| S003 | Cerrado en fase sintética | QQ es falsable para el modelo proyectivo; no separa clases de modelos |

El puente con el Laboratorio Cuántico-Junguiano queda en suspenso: ningún experimento ha mostrado todavía una señal quantum-like que lo justifique.
