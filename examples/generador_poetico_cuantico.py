"""
Generador Poético Cuántico

Un poeta cuántico-saussureano que genera versos a partir de
superposiciones de palabras y colapsos probabilísticos.
"""

import random
import copy
import numpy as np
from saussure_quantum import SignoCuanto, Langue
from saussure_quantum.collapse import colapso_parole, ContextoEnunciativo
from saussure_quantum.operators import operador_diferencia
from saussure_quantum.lexicon import cargar_lexicon, RUTA_LEXICON_DEFAULT

# Diccionario de juguete (6 palabras por categoría): se usa solo si no hay
# léxico real disponible en saussure_quantum/recursos/lexicon_es.json
# (generado con `python saussure_quantum/lexicon.py` a partir de
# UD_Spanish-AnCora).
DICCIONARIO_JUGUETE = {
    "sustantivos": (
        ["amor", "caos", "luz", "sombra", "infinito", "vacío"],
        [1, 1.2, 0.8, 0.9, 1.1, 0.7],
    ),
    "verbos": (
        ["nace", "muere", "sueña", "vuela", "cae", "asciende"],
        [1, 0.9, 1.3, 0.8, 0.6, 1.1],
    ),
    "adjetivos": (
        ["eterno", "fugaz", "profundo", "ligero", "oscuro", "brillante"],
        [1.2, 0.8, 0.7, 1.1, 0.9, 1.3],
    ),
    "conectores": (
        ["y", "o", "pero", "cuando", "donde", "como"],
        [1.5, 0.5, 0.8, 1.2, 0.6, 0.9],
    ),
}


class PoetaCuantico:
    """
    Poeta que escribe versos usando colapsos cuánticos.

    Cada palabra comienza en superposición y colapsa
    al ser "dicha" (escrita).
    """

    def __init__(self, nombre: str = "Quantum Poet", ruta_lexicon=RUTA_LEXICON_DEFAULT):
        """
        Args:
            nombre: Nombre del poeta
            ruta_lexicon: Ruta al léxico real (JSON categoria -> [(lema, frecuencia)]).
                Si el archivo no existe, usa el diccionario de juguete original.
        """
        self.nombre = nombre
        self.historial = []
        self.usando_lexicon_real = False

        try:
            lexicon = cargar_lexicon(ruta_lexicon)
            self.diccionario = self._diccionario_desde_lexicon(lexicon)
            self.usando_lexicon_real = True
        except (FileNotFoundError, OSError):
            self.diccionario = {
                categoria: SignoCuanto(palabras, amplitudes)
                for categoria, (palabras, amplitudes) in DICCIONARIO_JUGUETE.items()
            }

    @staticmethod
    def _diccionario_desde_lexicon(lexicon) -> dict:
        """
        Construye un SignoCuanto por categoría a partir de (lema, frecuencia).

        Amplitud = sqrt(frecuencia): como SignoCuanto normaliza por norma L2,
        la probabilidad de colapso de cada lema queda proporcional a su
        frecuencia relativa en el corpus (P = |amplitud|² ∝ frecuencia).
        """
        diccionario = {}
        for categoria, entradas in lexicon.items():
            if not entradas:
                continue
            palabras = [lema for lema, _ in entradas]
            amplitudes = [np.sqrt(freq) for _, freq in entradas]
            diccionario[categoria] = SignoCuanto(palabras, amplitudes)
        return diccionario
    
    def palabra_aleatoria(self, categoria: str, humor: float = 1.0) -> str:
        """
        Genera una palabra colapsando una categoría.

        Args:
            categoria: "sustantivos", "verbos", "adjetivos", "conectores"
            humor: Temperatura semántica (1.0 = normal, >1 = más caótico)
        """
        if categoria not in self.diccionario:
            return "?"

        # deepcopy para que cualquier mutación del SignoCuanto (ej. llamada directa
        # a .colapsar()) no corrompa el estado del diccionario compartido entre poemas.
        signo = copy.deepcopy(self.diccionario[categoria])
        contexto = ContextoEnunciativo(temperatura_semantica=humor)

        palabra, _, info = colapso_parole(signo, contexto)
        return palabra
    
    def generar_verso(self, estructura: list, humor: float = 1.0) -> str:
        """
        Genera un verso con una estructura dada.
        
        Args:
            estructura: Lista de categorías, ej: ["sustantivos", "verbos", "adjetivos"]
            humor: Temperatura semántica
        
        Returns:
            Verso generado
        """
        palabras = []
        for cat in estructura:
            palabra = self.palabra_aleatoria(cat, humor)
            palabras.append(palabra)
        
        verso = " ".join(palabras)
        verso = verso[0].upper() + verso[1:]  # Capitalizar
        self.historial.append(verso)
        return verso
    
    def generar_poema(self, num_versos: int = 4, humor_inicial: float = 1.0) -> str:
        """
        Genera un poema completo.
        
        El humor puede variar a lo largo del poema.
        """
        poema = []
        
        for i in range(num_versos):
            # Variación de humor (cada verso puede ser diferente)
            humor = humor_inicial * (0.8 + 0.4 * np.sin(i))
            
            # Estructuras alternativas para variedad
            estructuras = [
                ["sustantivos", "verbos", "adjetivos"],
                ["adjetivos", "sustantivos", "verbos"],
                ["verbos", "sustantivos"],
                ["conectores", "adjetivos", "sustantivos", "verbos"]
            ]
            
            estructura = random.choice(estructuras)
            verso = self.generar_verso(estructura, humor)
            poema.append(verso)
        
        return "\n".join(poema)
    
    def estado_poetico(self) -> dict:
        """
        Analiza el estado cuántico del poeta.
        
        Returns:
            Estadísticas de los poemas generados
        """
        if not self.historial:
            return {"poemas_generados": 0}
        
        # Frecuencia de palabras usadas
        palabras = []
        for verso in self.historial:
            palabras.extend(verso.lower().split())
        
        frecuencias = {}
        for p in palabras:
            frecuencias[p] = frecuencias.get(p, 0) + 1
        
        return {
            "poemas_generados": len(self.historial),
            "palabras_totales": len(palabras),
            "vocabulario_unico": len(frecuencias),
            "palabra_mas_usada": max(frecuencias, key=frecuencias.get) if frecuencias else None
        }


def ejemplo_principio_diferencia():
    """
    Ejemplo del principio de diferencia aplicado a poesía.
    """
    print("\n" + "="*60)
    print("PRINCIPIO DE DIFERENCIA EN POESÍA")
    print("="*60)
    
    # Una palabra aislada (sin contexto)
    palabra_aislada = SignoCuanto(["amor", "odio", "indiferencia"], [1, 0, 0])
    
    # La misma palabra en oposición con otras
    amor = SignoCuanto(["amor", "odio", "indiferencia"], [1, 0, 0])
    odio = SignoCuanto(["amor", "odio", "indiferencia"], [0, 1, 0])
    indiferencia = SignoCuanto(["amor", "odio", "indiferencia"], [0, 0, 1])
    
    diferencia = operador_diferencia([amor, odio, indiferencia])
    
    print("\n📖 Una palabra aislada (no tiene sentido):")
    print(amor)
    
    print("\n📖 La misma palabra en el sistema de diferencias:")
    print(diferencia)
    print("\n'El amor ES porque NO ES odio ni indiferencia'")
    print("   → Saussure demostrado cuánticamente")


def main():
    """Función principal de demostración"""
    
    print("="*60)
    print("🎭 BIENVENIDO AL POETA CUÁNTICO-SAUSSUREANO 🎭")
    print("="*60)
    
    # Demostración del principio de diferencia
    ejemplo_principio_diferencia()
    
    # Crear poeta
    poeta = PoetaCuantico("Neurona Cuántica")

    print("\n" + "="*60)
    print("LÉXICO CARGADO")
    print("="*60)
    fuente = "real (UD_Spanish-AnCora)" if poeta.usando_lexicon_real else "juguete (6 palabras/categoría)"
    print(f"  Fuente: {fuente}")
    for categoria, signo in poeta.diccionario.items():
        print(f"  {categoria}: {signo.dimension} palabras")

    # Generar poemas con diferentes humores
    print("\n" + "="*60)
    print("POEMA 1: HUMOR NORMAL (ℏ = 1.0)")
    print("="*60)
    print(poeta.generar_poema(num_versos=4, humor_inicial=1.0))
    
    print("\n" + "="*60)
    print("POEMA 2: HUMOR ALTO (Caos semántico)")
    print("="*60)
    print(poeta.generar_poema(num_versos=4, humor_inicial=2.5))
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS DEL POETA")
    print("="*60)
    stats = poeta.estado_poetico()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("✨ CONCEPTO FINAL ✨")
    print("="*60)
    print("Cada palabra nace de una superposición cuántica")
    print("y colapsa en el acto de ser dicha.")
    print("La poesía es la huella de esos colapsos.")
    print("\n   — Fusión Saussure × Quantum —")


if __name__ == "__main__":
    main()