"""
simulador_indeterminacion.py
Simulador del principio de incertidumbre Saussure-Heisenberg

Una herramienta interactiva para explorar cómo no se puede conocer
simultáneamente el valor paradigmático y sintagmático de un signo.
"""

import numpy as np
import matplotlib.pyplot as plt
from saussure_quantum import SignoCuanto, Langue
from saussure_quantum.uncertainty import (
    PrincipioIncertidumbreSaussure,
    incertidumbre_saussure_heisenberg
)



class SimuladorIndeterminacion:
    """
    Simulador interactivo del principio de incertidumbre lingüístico.
    """
    
    def __init__(self, dimension=20):
        self.dimension = dimension
        self.langue = Langue(dimension, "Sistema de prueba")
        self.principio = PrincipioIncertidumbreSaussure(self.langue)
        self.historial = []
    
    def estado_sintagmatico(self, posicion):
        """Crea un estado con posición (sintagma) definida"""
        return self.principio.estado_sintagmatico_puro(posicion)
    
    def estado_paradigmatico(self, momento):
        """Crea un estado con momento (paradigma) definido"""
        return self.principio.estado_paradigmatico_puro(momento)
    
    def estado_coherente(self):
        """Crea un estado de mínima incertidumbre"""
        return self.principio.obs.estado_minima_incertidumbre()
    
    def analizar(self, estado):
        """Analiza un estado y muestra sus incertidumbres"""
        analisis = self.principio.analizar_estado(estado)
        
        print("\n" + "="*50)
        print("ANÁLISIS DE INCERTIDUMBRE")
        print("="*50)
        print(f"ΔS (incertidumbre sintagmática): {analisis['delta_sintagma']:.4f}")
        print(f"ΔP (incertidumbre paradigmática): {analisis['delta_paradigma']:.4f}")
        print(f"ΔS · ΔP = {analisis['producto_incertidumbre']:.4f}")
        print(f"Cota de Robertson ½|⟨[S,P]⟩| = {analisis['cota_robertson']:.4f}")
        print(f"Factor sobre cota: {analisis['factor_sobre_cota']:.2f}x")
        print(f"Interpretación: {analisis['interpretacion']}")
        print(f"Dominancia: {analisis['dominancia']}")
        
        return analisis
    
    def visualizar(self, estado, titulo="Estado lingüístico"):
        """Visualiza el estado en sus dos representaciones"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Sintagma (posición)
        probs_s = np.abs(estado.amplitudes)**2
        axes[0].bar(range(self.dimension), probs_s, color='steelblue', alpha=0.7)
        axes[0].set_title(f'{titulo}\n[Sintagma - Posición en la frase]')
        axes[0].set_xlabel('Posición')
        axes[0].set_ylabel('Probabilidad')
        axes[0].set_ylim(0, max(probs_s) * 1.1)
        
        # Paradigma (momento) - transformada de Fourier
        psi = estado.amplitudes
        momento = np.fft.fft(psi)
        probs_p = np.abs(momento)**2 / len(momento)
        axes[1].bar(range(self.dimension), probs_p, color='coral', alpha=0.7)
        axes[1].set_title('Paradigma - Capacidad de sustitución')
        axes[1].set_xlabel('Modo paradigmático')
        axes[1].set_ylabel('Probabilidad')
        axes[1].set_ylim(0, max(probs_p) * 1.1)
        
        plt.tight_layout()
        plt.show()
    
    def experimentar(self, tipo, parametro):
        """Ejecuta un experimento con un tipo de estado"""
        if tipo == "sintagma":
            estado = self.estado_sintagmatico(parametro)
            nombre = f"Sintagma definido (posición={parametro})"
        elif tipo == "paradigma":
            estado = self.estado_paradigmatico(parametro)
            nombre = f"Paradigma definido (modo={parametro})"
        elif tipo == "coherente":
            estado = self.estado_coherente()
            nombre = "Mínima incertidumbre"
        else:
            raise ValueError("Tipo debe ser 'sintagma', 'paradigma' o 'coherente'")
        
        print(f"\n📊 Experimentando con: {nombre}")
        self.visualizar(estado, nombre)
        analisis = self.analizar(estado)
        
        self.historial.append({
            "tipo": tipo,
            "parametro": parametro,
            "nombre": nombre,
            "delta_s": analisis['delta_sintagma'],
            "delta_p": analisis['delta_paradigma'],
            "producto": analisis['producto_incertidumbre']
        })
        
        return estado
    
    def mostrar_comparacion(self):
        """Muestra comparación de todos los experimentos realizados"""
        if not self.historial:
            print("No hay experimentos aún.")
            return
        
        print("\n" + "="*60)
        print("COMPARACIÓN DE EXPERIMENTOS")
        print("="*60)
        print(f"{'Experimento':<30} {'ΔS':<10} {'ΔP':<10} {'ΔS·ΔP':<10}")
        print("-"*60)
        
        for exp in self.historial:
            nombre = exp['nombre'][:28]
            print(f"{nombre:<30} {exp['delta_s']:<10.4f} {exp['delta_p']:<10.4f} {exp['producto']:<10.4f}")
    
    def demostracion_completa(self):
        """Ejecuta una demostración completa del principio"""
        print("\n" + "="*60)
        print("DEMOSTRACIÓN DEL PRINCIPIO DE INCERTIDUMBRE")
        print("SAUSSURE-HEISENBERG")
        print("="*60)
        print("""
Este principio establece que NO se puede conocer simultáneamente
con precisión absoluta:

  • La POSICIÓN de un signo en la frase (Sintagma)
  • Su CAPACIDAD DE SUSTITUCIÓN (Paradigma)

A continuación, demostramos esta complementariedad.
""")
        
        input("Presiona Enter para comenzar la demostración...")
        
        # Caso 1: Sintagma bien definido
        print("\n🔵 CASO 1: SINTAGMA PERFECTAMENTE DEFINIDO")
        print("   Sabemos EXACTAMENTE dónde aparece la palabra")
        estado1 = self.experimentar("sintagma", 5)
        
        input("\nPresiona Enter para continuar...")
        
        # Caso 2: Paradigma bien definido
        print("\n🔴 CASO 2: PARADIGMA PERFECTAMENTE DEFINIDO")
        print("   Sabemos EXACTAMENTE qué palabras pueden reemplazarla")
        estado2 = self.experimentar("paradigma", 3)
        
        input("\nPresiona Enter para continuar...")
        
        # Caso 3: Mínima incertidumbre
        print("\n🟢 CASO 3: MÍNIMA INCERTIDUMBRE (COMPROMISO)")
        print("   Estado gaussiano de referencia (no minimiza el producto)")
        estado3 = self.experimentar("coherente", None)
        
        print("\n" + "="*60)
        print("CONCLUSIÓN")
        print("="*60)
        print("""
Un estado con sintagma exacto (ΔS = 0) tiene paradigma disperso
(ΔP = ℏ/√2), y una onda plana con paradigma exacto (ΔP = 0) tiene
sintagma disperso.

La cota que se cumple siempre es la de Robertson,
    ΔS·ΔP ≥ ½|⟨[S,P]⟩|,
que depende del estado y puede valer 0. En dimensión finita NO
existe la cota universal ℏ/2: en los dos casos puros el producto es 0.

Es una propiedad matemática de este par de operadores, usada como
analogía formal; no es una ley empírica del lenguaje.
""")


def menu_interactivo():
    """Menú interactivo para el simulador"""
    simulador = SimuladorIndeterminacion(dimension=20)
    
    while True:
        print("\n" + "="*50)
        print("SIMULADOR DE INCERTIDUMBRE LINGÜÍSTICA")
        print("="*50)
        print("1. Demostración completa")
        print("2. Experimentar con sintagma definido")
        print("3. Experimentar con paradigma definido")
        print("4. Experimentar con mínima incertidumbre")
        print("5. Ver comparación de experimentos")
        print("6. Salir")
        
        opcion = input("\nElige una opción (1-6): ").strip()
        
        if opcion == "1":
            simulador.demostracion_completa()
        
        elif opcion == "2":
            try:
                pos = int(input("Posición sintagmática (0-19): "))
                if 0 <= pos < 20:
                    simulador.experimentar("sintagma", pos)
                else:
                    print("Posición fuera de rango")
            except ValueError:
                print("Ingresa un número válido")
        
        elif opcion == "3":
            try:
                mom = int(input("Modo paradigmático (0-19): "))
                if 0 <= mom < 20:
                    simulador.experimentar("paradigma", mom)
                else:
                    print("Modo fuera de rango")
            except ValueError:
                print("Ingresa un número válido")
        
        elif opcion == "4":
            simulador.experimentar("coherente", None)
        
        elif opcion == "5":
            simulador.mostrar_comparacion()
        
        elif opcion == "6":
            print("\n¡Gracias por explorar el principio de incertidumbre!")
            print('Recuerda: "El ser es un efecto de la diferencia observada"\n')
            break
        
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu_interactivo()