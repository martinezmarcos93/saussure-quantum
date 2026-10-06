"""
operators.py - Operadores cuántico-semióticos

Implementa:
- Operador Diferencia (D̂): Materializa el principio saussureano de negatividad
- Observables para medición de diferencias
- Operadores de comparación semántica
"""

import numpy as np
from typing import List, Union, Optional, Tuple
from saussure_quantum.core import SignoCuanto, Langue


def operador_diferencia(estados: List[SignoCuanto], normalizar: bool = True) -> SignoCuanto:
    """
    Operador D̂: Aplica el principio de diferencia pura.
    
    D̂(|ψ₁⟩, |ψ₂⟩, ..., |ψₙ⟩) = Σ_{i<j} (|ψᵢ⟩ - |ψⱼ⟩)
    
    Esto materializa la idea saussureana de que un signo ES por NO SER
    todos los demás signos del sistema.
    
    Args:
        estados: Lista de estados cuántico-semióticos
        normalizar: Si True, normaliza el estado resultante
    
    Returns:
        Nuevo SignoCuanto que representa la pura diferencia
    
    Example:
        >>> fonema_p = SignoCuanto(["/p/"], [1])
        >>> fonema_b = SignoCuanto(["/b/"], [1])
        >>> diferencia = operador_diferencia([fonema_p, fonema_b])
        >>> # El resultado es el "ser por no ser"
    """
    if len(estados) < 2:
        raise ValueError("Se necesitan al menos 2 estados para la diferencia")

    # Verificar dimensión y que todos los significantes sean iguales.
    # Solo verificar dimensión no es suficiente: estados con etiquetas distintas
    # pero igual dimensión producirían un resultado con significantes arbitrarios
    # (los del primer estado) sin ninguna advertencia.
    dim = estados[0].dimension
    sigs_ref = estados[0].significantes
    for i, e in enumerate(estados[1:], start=1):
        if e.dimension != dim:
            raise ValueError(
                f"Todos los estados deben tener la misma dimensión. "
                f"estados[0].dimension={dim}, estados[{i}].dimension={e.dimension}"
            )
        if e.significantes != sigs_ref:
            raise ValueError(
                f"Todos los estados deben tener los mismos significantes. "
                f"estados[0].significantes={sigs_ref}, "
                f"estados[{i}].significantes={e.significantes}"
            )
    
    # Sumar todas las diferencias pares
    suma_amplitudes = np.zeros(dim, dtype=complex)
    
    for i in range(len(estados)):
        for j in range(i + 1, len(estados)):
            suma_amplitudes += (estados[i].amplitudes - estados[j].amplitudes)
    
    # Crear nuevo signo-cuanto
    # Usamos los significantes del primer estado como base
    significantes = estados[0].significantes.copy()
    resultado = SignoCuanto(significantes, suma_amplitudes)
    
    if normalizar:
        resultado.normalizar()
    
    return resultado


def operador_diferencia_matriz(langue: Langue) -> np.ndarray:
    """
    Construye la matriz del operador diferencia en la base de la langue.
    
    La matriz D tiene entradas D_ij = 1 para i≠j? (depende de la normalización)
    Representa el operador lineal que aplica diferencia a cualquier estado.
    
    Args:
        langue: Sistema lengua (espacio de Hilbert)
    
    Returns:
        Matriz D de dimensión d×d
    
    Note:
        D|ψ⟩ = Σ_j (|ψ⟩ - |eⱼ⟩⟨eⱼ|ψ⟩) = d·|ψ⟩ - Σ_j |eⱼ⟩⟨eⱼ|ψ⟩
        En base canónica: D = d·I - J (donde J es matriz de unos)
    """
    d = langue.dimension
    # Matriz identidad
    I = np.eye(d)
    # Matriz de unos (todos los elementos = 1)
    J = np.ones((d, d))
    # Operador diferencia: D = d·I - J
    D = d * I - J
    return D


class OperadorDiferencia:
    """
    Clase para manejar el operador diferencia como observable cuántico.
    
    Permite:
    - Aplicar el operador a estados
    - Medir el "valor de diferencia" de un signo
    - Calcular expectaciones
    """
    
    def __init__(self, langue: Langue):
        """
        Inicializar el operador diferencia sobre una langue específica.
        
        Args:
            langue: Sistema lengua sobre el que opera
        """
        self.langue = langue
        self.dimension = langue.dimension
        self._matriz = operador_diferencia_matriz(langue)
    
    def aplicar(self, estado: SignoCuanto) -> SignoCuanto:
        """
        Aplica el operador diferencia a un estado.
        
        D̂|ψ⟩ = d·|ψ⟩ - Σ_j |eⱼ⟩⟨eⱼ|ψ⟩
        
        Args:
            estado: Estado cuántico-semiótico
        
        Returns:
            Nuevo estado transformado por D̂
        """
        if estado.dimension != self.dimension:
            raise ValueError("Dimensión del estado incompatible con la langue")
        
        nuevas_amplitudes = self._matriz @ estado.amplitudes
        return SignoCuanto(estado.significantes.copy(), nuevas_amplitudes)
    
    def valor_esperado(self, estado: SignoCuanto) -> float:
        """
        Calcula ⟨ψ|D̂|ψ⟩, el valor esperado de la diferencia.
        
        Un valor alto indica que el estado está muy diferenciado
        de los estados base (más "pura diferencia").
        
        Args:
            estado: Estado cuántico-semiótico
        
        Returns:
            Valor real (expectación de un observable hermítico)
        """
        if estado.dimension != self.dimension:
            raise ValueError("Dimensión incompatible")
        
        # ⟨ψ|D̂|ψ⟩ = ψ† D ψ
        psi = estado.amplitudes
        valor = np.vdot(psi, self._matriz @ psi)
        return float(valor.real)
    
    def medir_diferencia(self, estado: SignoCuanto, seed: Optional[int] = None) -> Tuple[float, SignoCuanto]:
        """
        Mide el observable diferencia, colapsando el estado.
        
        Args:
            estado: Estado a medir
        
        Returns:
            (valor_medido, estado_colapsado)
        """
        # Calcular autovalores y autovectores
        eigenvals, eigenvecs = np.linalg.eigh(self._matriz)
        
        # Calcular probabilidades de cada autovalor
        psi = estado.amplitudes
        probabilidades = np.abs(eigenvecs.conj().T @ psi) ** 2
        
        # Seleccionar autovalor según probabilidad
        rng = np.random.default_rng(seed)
        idx = int(rng.choice(len(eigenvals), p=probabilidades))
        valor_medido = float(eigenvals[idx].real)
        
        # Colapsar al autovector correspondiente
        nuevo_estado = SignoCuanto(estado.significantes.copy(), eigenvecs[:, idx])
        
        return valor_medido, nuevo_estado
    
    def matriz(self) -> np.ndarray:
        """Retorna la matriz del operador"""
        return self._matriz.copy()
    
    def __repr__(self) -> str:
        return f"OperadorDiferencia({self.langue.nombre}, dim={self.dimension})"


def similitud_diferencial(estado1: SignoCuanto, estado2: SignoCuanto) -> float:
    """
    Calcula la similitud entre dos signos basada en sus diferencias.
    
    Cuanto más se parecen sus vectores de diferencia, más similares son.
    
    Args:
        estado1: Primer signo-cuanto
        estado2: Segundo signo-cuanto
    
    Returns:
        Similitud coseno entre 0 y 1
    """
    if estado1.dimension != estado2.dimension:
        raise ValueError("Dimensiones incompatibles")
    
    # La función es analítica: no debe mutar los estados de entrada.
    # Ambos estados se normalizan conceptualmente mediante sus normas locales.
    norma1 = np.linalg.norm(estado1.amplitudes)
    norma2 = np.linalg.norm(estado2.amplitudes)
    if norma1 <= 0 or norma2 <= 0:
        raise ValueError("No se puede calcular similitud con un estado nulo.")
    
    # Similitud coseno = |⟨ψ|φ⟩|
    solapamiento = abs(np.vdot(estado1.amplitudes, estado2.amplitudes)) / (norma1 * norma2)
    return float(np.clip(solapamiento, 0.0, 1.0))


def principio_negatividad(estado: SignoCuanto) -> dict:
    """
    Aplica el principio de negatividad esencial de Saussure.
    
    Analiza cómo el estado "es por no ser" los demás.
    
    Returns:
        Diccionario con análisis de negatividad
    """
    d = estado.dimension
    amplitudes = estado.amplitudes
    
    # Para cada significante, su "ser" es la negación de los otros
    negatividad = {}
    
    for i, sig in enumerate(estado.significantes):
        # Fuerza de ser por no ser los otros
        fuerza_negativa = sum(np.abs(amplitudes[j])**2 for j in range(d) if j != i)
        negatividad[sig] = fuerza_negativa
    
    return {
        "significante_principal": estado.significantes[np.argmax(np.abs(amplitudes))],
        "negatividad_por_significante": negatividad,
        "negatividad_total": sum(negatividad.values()),
        "estado": estado
    }


# Alias para facilidad de uso
D_hat = operador_diferencia
D_matrix = operador_diferencia_matriz