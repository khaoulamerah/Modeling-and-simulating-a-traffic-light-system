"""
Tests pour le module feux.py
Responsable : Sarah
"""

import pytest
import simpy
import sys
import os

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feux import SystemeFeux, ConfigurationFeux, CouleurFeu, EtatSysteme


def test_configuration_feux_defaut():
    """Test de la configuration par défaut"""
    config = ConfigurationFeux()
    assert config.duree_vert_a == 30.0
    assert config.duree_vert_b == 25.0
    assert config.duree_jaune == 3.0
    assert config.duree_pietons == 15.0
    assert config.duree_cycle == 76.0


def test_configuration_feux_personnalisee():
    """Test d'une configuration personnalisée"""
    config = ConfigurationFeux(
        duree_vert_a=28.0,
        duree_vert_b=28.0,
        duree_jaune=3.0,
        duree_pietons=14.0
    )
    assert config.duree_cycle == 76.0  # 28+3+28+3+14


def test_proportions_temps_vert():
    """Test des proportions de temps vert"""
    config = ConfigurationFeux()
    
    # Voie A : 30/76 ≈ 0.395
    assert abs(config.proportion_vert_a() - 0.395) < 0.001
    
    # Voie B : 25/76 ≈ 0.329
    assert abs(config.proportion_vert_b() - 0.329) < 0.001


def test_systeme_feux_initialisation():
    """Test de l'initialisation du système de feux"""
    env = simpy.Environment()
    systeme = SystemeFeux(env)
    
    # Vérifier l'état initial (S1 : Voie A verte)
    assert systeme.etat_actuel == EtatSysteme.S1
    assert systeme.feu_a.couleur == CouleurFeu.VERT
    assert systeme.feu_b.couleur == CouleurFeu.ROUGE
    assert systeme.nombre_cycles == 0


def test_cycle_complet():
    """Test d'un cycle complet des feux"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    systeme = SystemeFeux(env, config)
    
    # Lancer le cycle
    env.process(systeme.gerer_cycle())
    
    # Simuler un cycle complet
    env.run(until=config.duree_cycle)
    
    # Vérifier qu'un cycle est terminé
    assert systeme.nombre_cycles == 1
    
    # Vérifier qu'on est revenu à S1
    assert systeme.etat_actuel == EtatSysteme.S1


def test_peut_passer():
    """Test des fonctions peut_passer_voie_x"""
    env = simpy.Environment()
    systeme = SystemeFeux(env)
    
    # État initial S1 : Voie A verte
    assert systeme.peut_passer_voie_a() == True
    assert systeme.peut_passer_voie_b() == False


def test_historique_etats():
    """Test de l'enregistrement de l'historique"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    systeme = SystemeFeux(env, config)
    
    env.process(systeme.gerer_cycle())
    env.run(until=50)  # 50 secondes
    
    # Doit avoir enregistré des transitions
    assert len(systeme.historique_etats) > 0


def test_statistiques():
    """Test du calcul des statistiques"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    systeme = SystemeFeux(env, config)
    
    env.process(systeme.gerer_cycle())
    env.run(until=config.duree_cycle * 2)  # 2 cycles
    
    stats = systeme.obtenir_statistiques()
    
    assert stats['nombre_cycles'] == 2
    assert stats['duree_cycle'] == 76.0
    assert stats['temps_simulation'] >= config.duree_cycle * 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])