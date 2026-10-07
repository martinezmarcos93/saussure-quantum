"""
Unit tests for uncertainty.py
"""

import pytest
import numpy as np
from saussure_quantum.core import SignoCuanto, Langue
from saussure_quantum.uncertainty import (
    ObservablesSaussureanos,
    PrincipioIncertidumbreSaussure,
    incertidumbre_saussure_heisenberg,
    paradoja_del_observador_linguistico,
    HBAR_SEMIOTICO
)


class TestObservablesSaussureanos:
    """Pruebas para observables complementarios"""
    
    def test_initialization(self):
        """Test inicialización"""
        obs = ObservablesSaussureanos(5)
        assert obs.dimension == 5
        assert obs.S.shape == (5, 5)
        assert obs.P.shape == (5, 5)
    
    def test_sintagma_operator(self):
        """Test operador sintagma (posición)"""
        obs = ObservablesSaussureanos(4)
        # Debe ser diagonal con 0,1,2,3
        expected_S = np.diag([0, 1, 2, 3])
        assert np.allclose(obs.S, expected_S)
    
    def test_conmutacion(self):
        """
        Test del error de conmutación [S, P] - iℏ·I.

        La relación [S,P] = iℏI es matemáticamente imposible en dimensión
        finita (Tr([S,P])=0 pero Tr(iℏI)=iℏd ≠ 0), por lo que ninguna
        implementación discreta puede satisfacerla exactamente.
        Se verifica que el error cuantitativo sea finito, reproducible
        y acotado de forma razonable.
        """
        obs = ObservablesSaussureanos(5, hbar=1.0)
        error = obs.error_conmutacion()
        assert np.isfinite(error), "El error de conmutación debe ser finito"
        assert error > 0, "En dimensión finita el error siempre es positivo"
        # El error escala con sqrt(d) * hbar; para d=5 esperamos < 10
        assert error < 10.0, f"Error de conmutación inesperadamente alto: {error:.4f}"

    def test_conmutacion_hbar_custom(self):
        """El error de conmutación escala linealmente con hbar."""
        hbar = 2.0
        obs1 = ObservablesSaussureanos(5, hbar=1.0)
        obs2 = ObservablesSaussureanos(5, hbar=hbar)
        # Error debe escalar con hbar
        assert np.isclose(obs2.error_conmutacion(), hbar * obs1.error_conmutacion(), rtol=1e-6), \
            "El error de conmutación debe ser proporcional a hbar"
    
    def test_incertidumbre_estado_base(self):
        """Test incertidumbre para estado base"""
        obs = ObservablesSaussureanos(10)
        lang = Langue(10)
        estado = lang.estado_base(0)  # Sintagma puro
        
        delta_S, delta_P, producto = obs.incertidumbre(estado)
        
        # Delta_S debe ser 0 (posición definida)
        assert np.isclose(delta_S, 0.0, atol=1e-10)
        # ΔP es finita y vale exactamente ℏ/√2: <P>=0 y <P²>=Σ_j|P_j0|²=ℏ²/2.
        # (El test anterior exigía ΔP > 1 y ΔS·ΔP ≥ ℏ/2; ambas cosas son
        # falsas en dimensión finita: aquí el producto es exactamente 0.)
        assert np.isclose(delta_P, HBAR_SEMIOTICO / np.sqrt(2), atol=1e-12)
        assert np.isclose(producto, 0.0, atol=1e-12)
        # La cota correcta es la de Robertson, que para este estado es 0.
        psi = estado.amplitudes
        cota = 0.5 * abs(np.vdot(psi, obs._conmutador @ psi))
        assert np.isclose(cota, 0.0, atol=1e-12)
        assert producto >= cota - 1e-10
    
    def test_estado_minima_incertidumbre(self):
        """Test estado de mínima incertidumbre"""
        obs = ObservablesSaussureanos(20)
        estado = obs.estado_minima_incertidumbre()
        delta_S, delta_P, producto = obs.incertidumbre(estado)
        
        # La cota que debe cumplirse es la de Robertson, calculada con el
        # conmutador real. La cota canónica ℏ/2 no aplica en dimensión finita:
        # este estado tiene producto ≈ 0.4876 < 0.5 sin violar nada.
        psi = estado.amplitudes
        cota = 0.5 * abs(np.vdot(psi, obs._conmutador @ psi))
        assert producto >= cota - 1e-10, f"Viola Robertson: {producto} < {cota}"
        assert producto < HBAR_SEMIOTICO / 2, "Contraejemplo documentado de la cota canónica"
        assert np.isfinite(producto) and producto > 0


class TestPrincipioIncertidumbreSaussure:
    """Pruebas para el principio de incertidumbre"""
    
    def test_initialization(self):
        """Test inicialización"""
        lang = Langue(8)
        principio = PrincipioIncertidumbreSaussure(lang)
        assert principio.langue == lang
        assert principio.hbar == HBAR_SEMIOTICO
    
    def test_analizar_estado(self):
        """Test análisis de estado"""
        lang = Langue(10)
        principio = PrincipioIncertidumbreSaussure(lang)
        estado = lang.superposicion([1] * 10)
        
        analisis = principio.analizar_estado(estado)
        
        assert "delta_sintagma" in analisis
        assert "delta_paradigma" in analisis
        assert "producto_incertidumbre" in analisis
        assert "cota_robertson" in analisis
        assert "satisface_robertson" in analisis
        assert analisis["satisface_robertson"] is True
        # La superposición uniforme es autovector de P (k=0): ΔP = 0.
        assert np.isclose(analisis["delta_paradigma"], 0.0, atol=1e-10)
    
    def test_estado_sintagmatico_puro(self):
        """Test estado con sintagma puro"""
        lang = Langue(5)
        principio = PrincipioIncertidumbreSaussure(lang)
        estado = principio.estado_sintagmatico_puro(2)
        
        # Debe ser el estado base en índice 2
        assert np.isclose(estado.amplitudes[2], 1.0)
        assert np.sum(np.abs(estado.amplitudes)) == 1.0
        
        analisis = principio.analizar_estado(estado)
        assert np.isclose(analisis["delta_sintagma"], 0.0, atol=1e-10)
    
    def test_estado_paradigmatico_puro(self):
        """Test estado con paradigma puro"""
        lang = Langue(5)
        principio = PrincipioIncertidumbreSaussure(lang)
        estado = principio.estado_paradigmatico_puro(1)
        
        analisis = principio.analizar_estado(estado)
        # El momento debe estar bien definido (delta_P pequeño)
        assert analisis["delta_paradigma"] < 0.1
    
    def test_demostrar_principio(self):
        """Test demostración completa"""
        lang = Langue(10)
        principio = PrincipioIncertidumbreSaussure(lang)
        
        demo = principio.demostrar_principio()
        
        assert "sintagma_puro" in demo
        assert "paradigma_puro" in demo
        assert "minima_incertidumbre" in demo
        
        prod_min = demo["minima_incertidumbre"]["producto"]
        prod_sintagma = demo["sintagma_puro"]["producto"]
        prod_paradigma = demo["paradigma_puro"]["producto"]

        # Los dos estados puros tienen producto exactamente 0 (una de las dos
        # dispersiones se anula y la otra es finita). El test anterior suponía
        # que el sintagma puro tenía producto "infinito o muy grande".
        assert np.isclose(prod_sintagma, 0.0, atol=1e-10)
        assert np.isclose(prod_paradigma, 0.0, atol=1e-10)
        # El estado gaussiano de referencia NO minimiza el producto.
        assert np.isfinite(prod_min) and prod_min > prod_sintagma
        # Robertson se cumple en los tres casos.
        for caso in demo.values():
            assert caso["producto"] >= caso["cota_robertson"] - 1e-10


class TestFuncionesDeAltoNivel:
    """Pruebas para funciones helper"""
    
    def test_incertidumbre_saussure_heisenberg(self):
        """Test función principal"""
        estado = SignoCuanto(["x", "y", "z"], [1, 1, 1])
        resultado = incertidumbre_saussure_heisenberg(estado)
        
        assert "producto_incertidumbre" in resultado
        assert resultado["satisface_robertson"] is True
    
    def test_paradoja_observador(self):
        """Test paradoja del observador"""
        # Dimensión 3: es la mínima con operador paradigma no trivial.
        estado = SignoCuanto(["a", "b", "c"], [1, 1, 1])
        resultado = paradoja_del_observador_linguistico(estado)
        
        assert "estado_original" in resultado
        assert "despues_medir_sintagma" in resultado
        assert "despues_medir_paradigma" in resultado
        
        # Medir sintagma debe perturbar el paradigma
        perturbacion = resultado["despues_medir_sintagma"]["cambio_significativo"]
        assert isinstance(perturbacion, bool)
        # El estado uniforme tiene ΔP = 0; proyectar sobre S lo lleva a un
        # estado base con ΔP = ℏ/√2: la perturbación es real y medible.
        assert perturbacion is True
        assert np.isclose(resultado["despues_medir_sintagma"]["delta_P"], HBAR_SEMIOTICO / np.sqrt(2))
        # El indicador global se calcula; ya no es una constante True.
        assert resultado["perturbacion_observada"] is True
        assert "principio_demostrado" not in resultado

    def test_paradoja_observador_sin_perturbacion(self):
        """Un estado base ya es autoestado de S: medir S no altera nada."""
        estado = SignoCuanto(["a", "b", "c"], [1, 0, 0])
        resultado = paradoja_del_observador_linguistico(estado)
        assert resultado["despues_medir_sintagma"]["cambio_significativo"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])