"""
core.py - Clases base del sistema Saussure-Quantum

Contiene:
- SignoCuanto: Representación del signo lingüístico como estado cuántico
- Langue: El sistema de la lengua como espacio de Hilbert
"""

import numpy as np
from typing import List, Union, Optional, Dict, Any
import warnings


class SignoCuanto:
    """
    Signo lingüístico como estado cuántico.
    
    Un signo-cuanto es una superposición de significantes posibles,
    cada uno con una amplitud de probabilidad compleja.
    
    Attributes:
        significantes (List[str]): Lista de significantes posibles
        amplitudes (np.ndarray): Vector de amplitudes complejas
        dimension (int): Dimensión del espacio de Hilbert
    """
    
    def __init__(self, 
                 significantes: List[str], 
                 amplitudes: Optional[List[complex]] = None):
        """
        Inicializar un signo-cuanto.
        
        Args:
            significantes: Lista de etiquetas para los significantes
            amplitudes: Lista de amplitudes complejas (opcional)
                        Si es None, se crea superposición equitativa
        """
        if not significantes:
            raise ValueError("Se requiere al menos un significante.")
        if len(set(significantes)) != len(significantes):
            raise ValueError("Los significantes deben ser únicos.")
        self.significantes = list(significantes)
        self.dimension = len(significantes)
        
        if amplitudes is None:
            # Superposición equitativa: todos con misma amplitud
            amp = 1.0 / np.sqrt(self.dimension)
            self.amplitudes = np.ones(self.dimension, dtype=complex) * amp
        else:
            self.amplitudes = np.array(amplitudes, dtype=complex)
            
        self.normalizar()
    
    def normalizar(self) -> None:
        """Normalizar el vector de amplitudes (norma L2 = 1)"""
        norma = np.linalg.norm(self.amplitudes)
        if norma > 0 and np.isfinite(norma):
            self.amplitudes = self.amplitudes / norma
        else:
            raise ValueError("El vector de amplitudes debe tener norma finita y distinta de cero.")
    
    def probabilidad(self, significante: Union[str, int]) -> float:
        """
        Calcular probabilidad de colapsar a un significante específico.
        
        Args:
            significante: El significante (str) o su índice (int)
        
        Returns:
            Probabilidad (entre 0 y 1)
        """
        if isinstance(significante, str):
            try:
                idx = self.significantes.index(significante)
            except ValueError:
                raise ValueError(f"Significante '{significante}' no encontrado")
        else:
            idx = significante
            
        return float(np.abs(self.amplitudes[idx]) ** 2)
    
    def colapsar(self, idx: Optional[int] = None, seed: Optional[int] = None) -> tuple:
        """
        Acto de parole: colapsar la superposición a un significante.

        Retorna el significante resultante Y un nuevo SignoCuanto colapsado,
        sin modificar el estado original (inmutable, consistente con colapso_parole()).

        Args:
            idx: Índice específico (para pruebas) o None para muestreo probabilístico

        Returns:
            (significante, estado_colapsado) — tupla con el significante elegido
            y un nuevo SignoCuanto con amplitudes colapsadas al estado base idx.

        Note:
            Versiones anteriores mutaban self.amplitudes in-place y retornaban
            solo el str. La firma cambió a tupla para ser consistente con
            colapso_parole(). Si solo necesitás el significante: sig, _ = signo.colapsar()
        """
        if idx is not None and not 0 <= idx < self.dimension:
            raise IndexError(f"Índice de colapso fuera de rango: {idx}")
        if idx is None:
            probabilidades = np.abs(self.amplitudes) ** 2
            rng = np.random.default_rng(seed)
            idx = int(rng.choice(self.dimension, p=probabilidades))

        # Construir el estado colapsado como objeto nuevo, sin mutar self
        amplitudes_colapsadas = np.zeros(self.dimension, dtype=complex)
        amplitudes_colapsadas[idx] = 1.0
        estado_colapsado = SignoCuanto(self.significantes.copy(), amplitudes_colapsadas)

        return self.significantes[idx], estado_colapsado
    
    def densidad(self) -> np.ndarray:
        """
        Matriz densidad del estado puro.
        
        Returns:
            Matriz densidad ρ = |ψ⟩⟨ψ|
        """
        return np.outer(self.amplitudes, self.amplitudes.conj())
    
    def fase_relativa(self, i: int, j: int) -> float:
        """
        Calcular fase relativa entre dos significantes.
        
        Returns:
            Ángulo de fase en radianes
        """
        return np.angle(self.amplitudes[i] / self.amplitudes[j])
    
    def __repr__(self) -> str:
        return f"SignoCuanto({self.significantes[:3]}...)" if len(self.significantes) > 3 else f"SignoCuanto({self.significantes})"
    
    def __str__(self) -> str:
        """Representación legible del estado"""
        lines = [f"Signo-cuanto (d={self.dimension}):"]
        for i, sig in enumerate(self.significantes):
            prob = self.probabilidad(i) * 100
            amp = self.amplitudes[i]
            lines.append(f"  {sig}: |{amp:.3f}|² = {prob:.1f}%")
        return "\n".join(lines)


class Langue:
    """
    Sistema de la lengua como espacio de Hilbert.
    
    La langue es el conjunto de todas las diferencias potenciales,
    similar al espacio de estados de un sistema cuántico.
    """
    
    def __init__(self, dimension: int, nombre: str = "Langue",
                 terminos: Optional[List[str]] = None):
        """
        Inicializar el sistema lengua.

        Args:
            dimension: Dimensión del espacio de Hilbert
            nombre: Nombre identificador del sistema
            terminos: Etiquetas personalizadas para los términos base (opcional).
                      Si se omite, se generan automáticamente como "término_0", etc.
                      Debe tener exactamente `dimension` elementos si se provee.

        Example:
            >>> lang = Langue(3, terminos=["/p/", "/b/", "/t/"])
        """
        if terminos is not None and len(terminos) != dimension:
            raise ValueError(
                f"'terminos' debe tener {dimension} elementos, "
                f"pero se recibieron {len(terminos)}"
            )
        self.dimension = dimension
        self.nombre = nombre
        self._base = terminos if terminos is not None else [f"término_{i}" for i in range(dimension)]
    
    def estado_base(self, idx: int) -> SignoCuanto:
        """
        Crear un estado base (significante puro).
        
        Args:
            idx: Índice del término base
        
        Returns:
            SignoCuanto colapsado a ese término
        """
        amplitudes = np.zeros(self.dimension, dtype=complex)
        amplitudes[idx] = 1.0
        return SignoCuanto(self._base, amplitudes)
    
    def superposicion(self, coeficientes: List[complex]) -> SignoCuanto:
        """
        Crear un estado en superposición.
        
        Args:
            coeficientes: Coeficientes para cada término base
        
        Returns:
            SignoCuanto en superposición
        """
        if len(coeficientes) != self.dimension:
            raise ValueError(f"Se requieren {self.dimension} coeficientes")
        return SignoCuanto(self._base, coeficientes)
    
    def base_canonica(self) -> List[SignoCuanto]:
        """Obtener la base canónica del espacio"""
        return [self.estado_base(i) for i in range(self.dimension)]
    
    def producto_interno(self, psi: SignoCuanto, phi: SignoCuanto) -> complex:
        """
        Producto interno entre dos signos-cuanto.
        Representa la similitud semántica cuántica.
        """
        if psi.dimension != phi.dimension:
            raise ValueError("Dimensiones incompatibles")
        return np.vdot(psi.amplitudes, phi.amplitudes)
    
    def __repr__(self) -> str:
        return f"Langue('{self.nombre}', d={self.dimension})"