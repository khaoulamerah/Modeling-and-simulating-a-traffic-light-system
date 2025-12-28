"""Tests pour le module vehicule.py"""
import pytest
from src.vehicule import Vehicule, Direction, GenerateurVehicules
import simpy

def test_creation_vehicule():
    """Test de création d'un véhicule"""
    v = Vehicule(1, Direction.VOIE_A, 0.0)
    assert v.id == 1
    assert v.direction == Direction.VOIE_A
    assert v.temps_attente == 0.0

def test_generateur():
    """Test du générateur"""
    env = simpy.Environment()
    gen = GenerateurVehicules(env, 0.3, 0.3)
    
    # Générer 10 temps inter-arrivée
    temps = [gen.temps_inter_arrivee(0.3) for _ in range(10)]
    
    # Vérifier que la moyenne est proche de 1/λ = 3.33
    moyenne = sum(temps) / len(temps)
    assert 2.0 < moyenne < 5.0  # Marge pour l'aléatoire

if __name__ == "__main__":
    pytest.main([__file__])