"""
collapse.py - Parole como medición cuántica

Implementa:
- El acto de habla como colapso de la superposición lingüística
- Diferentes tipos de medición (fuerte, débil, parcial)
- Producción de realidad semiótica
- Observadores y contextos de enunciación
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from saussure_quantum.core import SignoCuanto, Langue


@dataclass
class ContextoEnunciativo:
    """
    Contexto del acto de parole (medición).
    
    Análogo al aparato de medición en mecánica cuántica.
    """
    # Exponente de afilado p_i ∝ p_i^(1/T): T<1 concentra, T=1 no altera, T>1 aplana.
    # Valores por debajo de 0.01 se tratan como 0.01 para evitar overflow numérico.
    temperatura_semantica: float = 1.0
    intencionalidad: Optional[List[float]] = None  # Sesgo hacia ciertos significantes
    ruido_ambiental: float = 0.0  # Magnitud de ruido añadido a la distribución

    def __post_init__(self):
        if not np.isfinite(self.temperatura_semantica) or self.temperatura_semantica <= 0:
            raise ValueError("temperatura_semantica debe ser un número finito > 0.")
        if not np.isfinite(self.ruido_ambiental) or not 0 <= self.ruido_ambiental <= 1:
            raise ValueError("ruido_ambiental debe estar en [0, 1].")
        if self.intencionalidad is not None:
            self.intencionalidad = np.asarray(self.intencionalidad, dtype=float)
            if self.intencionalidad.ndim != 1 or self.intencionalidad.size == 0:
                raise ValueError("intencionalidad debe ser un vector no vacío.")
            if not np.all(np.isfinite(self.intencionalidad)) or np.any(self.intencionalidad < 0):
                raise ValueError("intencionalidad debe contener valores finitos no negativos.")
            suma = float(np.sum(self.intencionalidad))
            if suma <= 0:
                raise ValueError("intencionalidad debe tener suma estrictamente positiva.")
            self.intencionalidad = self.intencionalidad / suma


def colapso_parole(
    estado: SignoCuanto, 
    contexto: Optional[ContextoEnunciativo] = None,
    indice_forzado: Optional[int] = None,
    seed: Optional[int] = None,
) -> Tuple[str, SignoCuanto, Dict[str, Any]]:
    """
    ACTO DE PAROLE: Colapsa la superposición lingüística a un significante.
    
    Esta función modela el momento en que un hablante actualiza el sistema
    lengua, produciendo una realidad semiótica concreta.
    
    Args:
        estado: Signo-cuanto en superposición (lengua potencial)
        contexto: Contexto enunciativo (aparato de medición)
        indice_forzado: Para pruebas, fuerza un resultado específico
        seed: Semilla del generador local. Mismo estado + mismo contexto +
              misma semilla producen exactamente el mismo resultado.

    Raises:
        ValueError: si la intencionalidad es incompatible con el estado
            (dimensión distinta o peso nulo sobre todo el soporte del estado).

    Returns:
        (significante_resultante, estado_colapsado, info_medicion)
    
    Example:
        >>> signo = SignoCuanto(["sol", "luna", "estrella"], [1, 0.5j, 0.7])
        >>> resultado, nuevo_estado, info = colapso_parole(signo)
        >>> print(f"Dijo: {resultado}")
    """
    if contexto is None:
        contexto = ContextoEnunciativo()
    
    if contexto.intencionalidad is not None and len(contexto.intencionalidad) != estado.dimension:
        raise ValueError("La intencionalidad debe tener la misma dimensión que el estado.")
    if indice_forzado is not None and not 0 <= indice_forzado < estado.dimension:
        raise IndexError(f"Índice forzado fuera de rango: {indice_forzado}")
    rng = np.random.default_rng(seed)

    # 1. Obtener probabilidades base del estado
    probabilidades_base = np.abs(estado.amplitudes) ** 2
    
    # 2. Aplicar contexto (distorsión de la medición)
    if contexto.intencionalidad is not None:
        # Sesgo intencional del hablante
        probabilidades = probabilidades_base * contexto.intencionalidad
        # Re-normalizar. Si la intención sólo pondera significantes con
        # probabilidad nula, el condicionamiento no está definido: antes se
        # ignoraba la intención en silencio y se devolvía la distribución base.
        if np.sum(probabilidades) <= 0:
            raise ValueError(
                "La intencionalidad asigna peso nulo a todos los significantes "
                "con probabilidad no nula en el estado."
            )
        probabilidades = probabilidades / np.sum(probabilidades)
    else:
        probabilidades = probabilidades_base
    
    # 3. Aplicar temperatura semántica (ruido)
    if contexto.temperatura_semantica != 1.0:
        # Distribución de Boltzmann modificada
        beta = 1.0 / max(contexto.temperatura_semantica, 0.01)
        probabilidades = probabilidades ** beta
        probabilidades = probabilidades / np.sum(probabilidades)
    
    # 4. Aplicar ruido ambiental
    if contexto.ruido_ambiental > 0:
        ruido = rng.uniform(0, contexto.ruido_ambiental, len(probabilidades))
        probabilidades = probabilidades + ruido
        probabilidades = probabilidades / np.sum(probabilidades)
    
    # 5. Seleccionar resultado
    if indice_forzado is not None:
        idx = indice_forzado
    else:
        idx = int(rng.choice(estado.dimension, p=probabilidades))
    
    # 6. Colapsar el estado.
    # Se construye el vector colapsado antes de llamar al constructor para
    # evitar el estado inconsistente que surgía de crear SignoCuanto(sigs, None)
    # (amplitudes uniformes + normalizar()) y luego sobreescribir .amplitudes
    # directamente, dejando el objeto temporalmente con norma cero.
    amplitudes_colapsadas = np.zeros(estado.dimension, dtype=complex)
    amplitudes_colapsadas[idx] = 1.0
    nuevo_estado = SignoCuanto(estado.significantes.copy(), amplitudes_colapsadas)
    
    # 7. Registrar información de la medición
    info = {
        "probabilidades_originales": probabilidades_base.tolist(),
        "probabilidades_modificadas": probabilidades.tolist(),
        "indice_seleccionado": idx,
        "contexto_utilizado": contexto,
        "incertidumbre_medicion": float(-np.sum(probabilidades * np.log(probabilidades + 1e-10)))
    }
    
    return estado.significantes[idx], nuevo_estado, info


class MedidorParole:
    """
    Medidor cuántico para el acto de habla.
    
    Permite realizar múltiples mediciones y mantener estadísticas
    del comportamiento del sistema lengua.
    """
    
    def __init__(self, contexto_base: Optional[ContextoEnunciativo] = None):
        """
        Inicializar medidor de parole.
        
        Args:
            contexto_base: Contexto por defecto para las mediciones
        """
        self.contexto_base = contexto_base or ContextoEnunciativo()
        self.historial = []
        self.estadisticas = {}
    
    def medir(
        self, 
        estado: SignoCuanto, 
        contexto: Optional[ContextoEnunciativo] = None,
        registrar: bool = True,
        seed: Optional[int] = None,
    ) -> Tuple[str, SignoCuanto]:
        """
        Realizar una medición (acto de parole).
        
        Args:
            estado: Estado a medir
            contexto: Contexto específico (opcional)
            registrar: Si se guarda en historial
            seed: Semilla opcional para una medición reproducible

        Returns:
            (significante, estado_colapsado)
        """
        ctx = contexto or self.contexto_base
        resultado, nuevo_estado, info = colapso_parole(estado, ctx, seed=seed)
        
        if registrar:
            self.historial.append({
                "estado_inicial": estado.amplitudes.copy(),
                "contexto": ctx,
                "resultado": resultado,
                "info": info
            })
            self._actualizar_estadisticas(resultado)
        
        return resultado, nuevo_estado
    
    def _actualizar_estadisticas(self, resultado: str):
        """Actualizar contadores estadísticos"""
        if resultado not in self.estadisticas:
            self.estadisticas[resultado] = 0
        self.estadisticas[resultado] += 1
    
    def medir_multiples(
        self, 
        estado: SignoCuanto, 
        n_mediciones: int,
        contexto: Optional[ContextoEnunciativo] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Realizar múltiples mediciones del mismo estado.
        
        Útil para estudiar la distribución de colapsos.
        
        Args:
            estado: Estado a medir
            n_mediciones: Número de actos de parole
            contexto: Contexto (opcional)
            seed: Semilla opcional; con semilla, las frecuencias son reproducibles

        Returns:
            Frecuencias relativas de cada significante
        """
        if isinstance(n_mediciones, bool) or not isinstance(n_mediciones, (int, np.integer)) or n_mediciones < 1:
            raise ValueError("n_mediciones debe ser un entero >= 1.")
        semillas = _semillas_hijas(seed, n_mediciones)
        resultados = []
        estado_original = SignoCuanto(estado.significantes.copy(), estado.amplitudes.copy())
        
        for i in range(n_mediciones):
            # Restaurar estado original antes de cada medición
            estado_actual = SignoCuanto(estado_original.significantes.copy(), estado_original.amplitudes.copy())
            resultado, _ = self.medir(estado_actual, contexto, registrar=False, seed=semillas[i])
            resultados.append(resultado)
        
        # Calcular frecuencias
        frecuencias = {}
        for r in resultados:
            frecuencias[r] = frecuencias.get(r, 0) + 1
        
        for k in frecuencias:
            frecuencias[k] /= n_mediciones
        
        return frecuencias
    
    def reset(self):
        """Reiniciar historial y estadísticas"""
        self.historial = []
        self.estadisticas = {}
    
    def entropia_parole(self) -> float:
        """
        Calcular entropía del sistema parole.
        
        Mayor entropía = mayor indeterminación en los actos de habla.
        """
        if not self.estadisticas:
            return 0.0
        
        total = sum(self.estadisticas.values())
        probs = [c/total for c in self.estadisticas.values()]
        return -np.sum([p * np.log(p) for p in probs if p > 0])


def _semillas_hijas(seed: Optional[int], n: int) -> List[Optional[int]]:
    """Deriva n semillas independientes de una semilla madre (None → sin semilla)."""
    if seed is None:
        return [None] * n
    return [int(x) for x in np.random.default_rng(seed).integers(0, 2**63 - 1, size=n)]


def medicion_debil(
    estado: SignoCuanto,
    fuerza: float = 0.3,
    n_pasos: int = 5,
    seed: Optional[int] = None,
) -> Tuple[str, SignoCuanto, List[Dict]]:
    """
    Mediciones débiles sucesivas (colapso gradual).

    Simula cómo un significado puede emerger gradualmente
    en lugar de colapsar instantáneamente.

    Cada paso aplica un operador de contracción parcial: las componentes
    con mayor probabilidad se refuerzan ligeramente y las débiles decaen,
    reduciendo la entropía de forma progresiva hasta el colapso final.

    La fórmula de contracción es:
        peso_i = (1 - fuerza) + fuerza * prob_i
    lo que garantiza peso_i ∈ (1-fuerza, 1), es decir, siempre < 1
    para las componentes débiles → contracción genuina hacia la dominante.

    Args:
        estado: Estado inicial en superposición
        fuerza: Intensidad de cada contracción, en [0, 1].
                0 = sin efecto. 1 = contracción máxima por paso (peso_i = prob_i),
                que NO equivale a un colapso inmediato: desde amplitudes
                proporcionales a (3, 2, 1) un paso con fuerza 1 deja
                probabilidades ≈ (0.918, 0.081, 0.001).
        n_pasos: Número de contracciones (entero >= 0) antes del colapso final
        seed: Semilla del colapso final. Las contracciones son deterministas.

    Returns:
        (significante_final, estado_final, registro_de_evolucion)

    Nota epistemológica: esta función es un modelo heurístico de colapso
    gradual. No implementa una medición débil canónica mediante operadores
    POVM/Kraus y no debe interpretarse como tal.
    """
    if not np.isfinite(fuerza) or not 0 <= fuerza <= 1:
        raise ValueError("fuerza debe estar en [0, 1].")
    if isinstance(n_pasos, bool) or not isinstance(n_pasos, (int, np.integer)) or n_pasos < 0:
        raise ValueError("n_pasos debe ser un entero >= 0.")

    registro = []
    estado_actual = SignoCuanto(estado.significantes.copy(), estado.amplitudes.copy())

    for paso in range(n_pasos):
        probs = np.abs(estado_actual.amplitudes) ** 2

        # Pesos de contracción: ∈ (1-fuerza, 1) para cada componente.
        # Las componentes débiles (prob ≈ 0) reciben peso ≈ (1-fuerza) < 1 → decaen.
        # Las componentes fuertes (prob ≈ 1) reciben peso ≈ 1 → se mantienen.
        # Esto modela genuinamente el colapso parcial de una medición débil.
        pesos = (1 - fuerza) + fuerza * probs
        nuevas_amplitudes = estado_actual.amplitudes * pesos
        nuevas_amplitudes = nuevas_amplitudes / np.linalg.norm(nuevas_amplitudes)

        registro.append({
            "paso": paso,
            "amplitudes": nuevas_amplitudes.copy(),
            "entropia": -np.sum(probs * np.log(probs + 1e-10))
        })

        estado_actual.amplitudes = nuevas_amplitudes

    # Colapso final (medición fuerte)
    resultado_final, estado_final, _ = colapso_parole(estado_actual, seed=seed)

    return resultado_final, estado_final, registro


def realidades_alternativas(
    estado: SignoCuanto,
    n_realidades: int = 10,
    contexto: Optional[ContextoEnunciativo] = None,
    seed: Optional[int] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Genera múltiples realidades emergentes del mismo estado inicial.
    
    Ilustra cómo diferentes actos de parole producen diferentes
    realidades semióticas desde la misma lengua potencial.
    
    Args:
        estado: Estado inicial
        n_realidades: Número de realidades a generar
        contexto: Contexto enunciativo
        seed: Semilla opcional para reproducir el conjunto completo

    Returns:
        Diccionario con las realidades generadas
    """
    realidades = {}
    semillas = _semillas_hijas(seed, max(0, n_realidades))

    for i in range(n_realidades):
        # Copiar estado original
        estado_copia = SignoCuanto(estado.significantes.copy(), estado.amplitudes.copy())
        resultado, _, info = colapso_parole(estado_copia, contexto, seed=semillas[i])
        realidades[f"realidad_{i+1}"] = {
            "significante": resultado,
            "probabilidad_original": info["probabilidades_originales"][
                estado.significantes.index(resultado)
            ],
            "incertidumbre": info["incertidumbre_medicion"]
        }
    
    return realidades


# Alias conceptuales
habla = colapso_parole
acto_de_significacion = colapso_parole
emergencia_de_realidad = colapso_parole