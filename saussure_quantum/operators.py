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

    Propiedades matemáticas (verificadas en tests/test_propiedades_matematicas.py):

    - La suma por pares equivale a Σ_k (n − 1 − 2k)·|ψ_k⟩ con k = 0..n−1.
      El resultado depende del ORDEN de la lista y, para n impar, el estado
      central recibe coeficiente 0: no influye en absoluto.
    - No es el operador lineal de `operador_diferencia_matriz` (el laplaciano
      D = d·I − J, que actúa sobre las componentes de UN estado). Son dos
      construcciones distintas y no deben tratarse como equivalentes.
    - Si la combinación se anula (p. ej. estados idénticos) no existe estado
      normalizable y se lanza ValueError.

    Args:
        estados: Lista de estados cuántico-semióticos
        normalizar: Se conserva por compatibilidad. SignoCuanto normaliza
            siempre en el constructor, de modo que el resultado tiene norma 1
            también con normalizar=False.

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
    if np.linalg.norm(suma_amplitudes) <= 1e-12:
        raise ValueError(
            "La diferencia por pares es el vector nulo (p. ej. estados idénticos): "
            "no define un estado normalizable."
        )
    return SignoCuanto(significantes, suma_amplitudes)


def operador_diferencia_matriz(langue: Langue) -> np.ndarray:
    """
    Construye la matriz del operador diferencia en la base de la langue.
    
    D = d·I − J, con J la matriz de unos: D_ii = d − 1 y D_ij = −1 para i ≠ j.

    Args:
        langue: Sistema lengua (espacio de Hilbert)

    Returns:
        Matriz D de dimensión d×d

    Note:
        Actúa sobre las componentes de un estado como una diferencia de cada
        una contra todas las demás:

            (D ψ)_i = Σ_j (ψ_i − ψ_j).

        Es el laplaciano del grafo completo K_d. Con |u⟩ = (1,…,1)/√d,

            D = d·(I − |u⟩⟨u|),

        es decir, d veces el proyector sobre el complemento de la superposición
        uniforme. Autovalores: 0 (autovector |u⟩) y d (degeneración d − 1).

        Una versión anterior de esta nota escribía D|ψ⟩ = d|ψ⟩ − Σ_j |e_j⟩⟨e_j|ψ⟩;
        eso es incorrecto, porque Σ_j |e_j⟩⟨e_j| = I (no J) y daría (d − 1)|ψ⟩.
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
        Aplica el operador diferencia a un estado y renormaliza.

        D̂|ψ⟩ = d·(|ψ⟩ − |u⟩⟨u|ψ⟩): elimina la componente uniforme.

        Args:
            estado: Estado cuántico-semiótico

        Returns:
            Nuevo estado transformado por D̂ (normalizado)

        Raises:
            ValueError: si el estado es la superposición uniforme (núcleo de
                D̂): D̂|u⟩ = 0 y no existe estado normalizable.
        """
        if estado.dimension != self.dimension:
            raise ValueError("Dimensión del estado incompatible con la langue")

        nuevas_amplitudes = self._matriz @ estado.amplitudes
        if np.linalg.norm(nuevas_amplitudes) <= 1e-12:
            raise ValueError(
                "El estado pertenece al núcleo de D̂ (superposición uniforme): "
                "D̂|ψ⟩ = 0 no define un estado normalizable."
            )
        return SignoCuanto(estado.significantes.copy(), nuevas_amplitudes)
    
    def valor_esperado(self, estado: SignoCuanto) -> float:
        """
        Calcula ⟨ψ|D̂|ψ⟩, el valor esperado de la diferencia.
        
        ⟨ψ|D̂|ψ⟩ = d·(1 − |⟨u|ψ⟩|²) ∈ [0, d]: mide cuánto se aparta el estado
        de la superposición uniforme |u⟩. Vale 0 para |u⟩, d − 1 para cualquier
        estado base y d para estados ortogonales a |u⟩.
        
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

        Medición proyectiva con la regla de Lüders: el estado posterior es la
        proyección de |ψ⟩ sobre el autoespacio del valor obtenido,
        P_λ|ψ⟩ / ‖P_λ|ψ⟩‖. El autovalor d está degenerado (d − 1 veces), por lo
        que colapsar a "un autovector" de `eigh` dentro de ese autoespacio
        —como hacía la versión anterior— dependía de una elección arbitraria
        de base de LAPACK y no del estado medido.

        Args:
            estado: Estado a medir
            seed: Semilla opcional para reproducibilidad

        Returns:
            (valor_medido, estado_colapsado)
        """
        if estado.dimension != self.dimension:
            raise ValueError("Dimensión del estado incompatible con la langue")

        eigenvals, eigenvecs = np.linalg.eigh(self._matriz)
        psi = estado.amplitudes

        # Agrupar autovectores por autovalor (autoespacios) dentro de tolerancia.
        grupos: List[Tuple[float, np.ndarray]] = []
        for k, valor in enumerate(eigenvals):
            if grupos and abs(valor - grupos[-1][0]) < 1e-8:
                grupos[-1] = (grupos[-1][0], np.column_stack([grupos[-1][1], eigenvecs[:, k]]))
            else:
                grupos.append((float(valor), eigenvecs[:, [k]]))

        proyecciones = [base @ (base.conj().T @ psi) for _, base in grupos]
        probabilidades = np.array([np.vdot(v, v).real for v in proyecciones])
        probabilidades = probabilidades / probabilidades.sum()

        rng = np.random.default_rng(seed)
        idx = int(rng.choice(len(grupos), p=probabilidades))
        valor_medido = float(round(grupos[idx][0], 10) + 0.0)
        nuevo_estado = SignoCuanto(estado.significantes.copy(), proyecciones[idx])

        return valor_medido, nuevo_estado
    
    def matriz(self) -> np.ndarray:
        """Retorna la matriz del operador"""
        return self._matriz.copy()
    
    def __repr__(self) -> str:
        return f"OperadorDiferencia({self.langue.nombre}, dim={self.dimension})"


def similitud_diferencial(estado1: SignoCuanto, estado2: SignoCuanto) -> float:
    """
    Solapamiento |⟨ψ|φ⟩| entre dos signos (raíz de la fidelidad).

    Pese al nombre histórico, no utiliza el operador diferencia: es el módulo
    del producto interno, invariante ante fases globales. Vale 1 para estados
    iguales salvo fase y 0 para estados ortogonales.

    Args:
        estado1: Primer signo-cuanto
        estado2: Segundo signo-cuanto

    Returns:
        Solapamiento entre 0 y 1
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

    La "negatividad" de cada significante es 1 − pᵢ (la probabilidad de los
    demás). Por construcción `negatividad_total` = d − 1 para todo estado
    normalizado: es una constante de la dimensión, no una medida que
    distinga estados. La información está en el reparto por significante.

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