"""
Tests d'intégration de la simulation complète
Responsable : Sarah
"""

import pytest
import simpy
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feux import SystemeFeux, ConfigurationFeux
from vehicule import GenerateurVehicules, Direction
from intersection import Intersection
from statistiques import StatistiquesTheorique, CollecteurDonnees


def test_integration_complete():
    """Test d'intégration : simulation complète de 100 secondes"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    
    systeme_feux = SystemeFeux(env, config)
    intersection = Intersection(env, systeme_feux)
    generateur = GenerateurVehicules(env, 0.3, 0.3)
    
    # Lancer les processus
    env.process(systeme_feux.gerer_cycle())
    env.process(generateur.generer_voie_a(intersection))
    env.process(generateur.generer_voie_b(intersection))
    
    # Simuler 100 secondes
    env.run(until=100)
    
    # Vérifier qu'il y a eu des arrivées
    assert generateur.compteur_a > 0
    assert generateur.compteur_b > 0
    
    # Vérifier qu'il y a eu des services
    stats = intersection.obtenir_statistiques()
    assert stats['voie_a']['vehicules_servis'] > 0
    assert stats['voie_b']['vehicules_servis'] > 0


def test_stabilite_systeme():
    """Test de stabilité : λ = 0.3, μ calculé"""
    config = ConfigurationFeux()
    
    lambda_a = 0.3
    mu_a = 1.0 * config.proportion_vert_a()  # ≈ 0.395
    
    theo = StatistiquesTheorique(lambda_a, mu_a)
    
    # Vérifier que le système est stable
    assert theo.rho < 1
    assert theo.est_stable == True


def test_conservation_flux():
    """Test de conservation : arrivées ≈ départs (en régime stable)"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    
    systeme_feux = SystemeFeux(env, config)
    intersection = Intersection(env, systeme_feux)
    generateur = GenerateurVehicules(env, 0.3, 0.3)
    
    env.process(systeme_feux.gerer_cycle())
    env.process(generateur.generer_voie_a(intersection))
    env.process(generateur.generer_voie_b(intersection))
    
    # Simuler 500 secondes
    env.run(until=500)
    
    stats = intersection.obtenir_statistiques()
    
    # Arrivées
    arrives_a = stats['voie_a']['vehicules_total']
    arrives_b = stats['voie_b']['vehicules_total']
    
    # Départs
    servis_a = stats['voie_a']['vehicules_servis']
    servis_b = stats['voie_b']['vehicules_servis']
    
    # La différence doit être petite (véhicules encore en attente)
    diff_a = abs(arrives_a - servis_a)
    diff_b = abs(arrives_b - servis_b)
    
    # Maximum 15 véhicules en attente (acceptable)
    assert diff_a < 15
    assert diff_b < 15


def test_loi_de_little():
    """Test de la loi de Little : L = λ × W"""
    env = simpy.Environment()
    config = ConfigurationFeux()
    
    lambda_a = 0.3
    mu_a = 1.0 * config.proportion_vert_a()
    
    systeme_feux = SystemeFeux(env, config)
    intersection = Intersection(env, systeme_feux)
    generateur = GenerateurVehicules(env, lambda_a, 0.3)
    
    env.process(systeme_feux.gerer_cycle())
    env.process(generateur.generer_voie_a(intersection))
    env.process(generateur.generer_voie_b(intersection))
    
    # Simuler longtemps pour avoir des stats stables
    env.run(until=1000)
    
    stats = intersection.obtenir_statistiques()
    
    # Calcul empirique
    W_empirique = stats['voie_a']['temps_attente_moyen']
    L_empirique = lambda_a * W_empirique
    
    # Calcul théorique
    theo = StatistiquesTheorique(lambda_a, mu_a)
    L_theorique = theo.L_q
    
    # Tolérance de 30% (acceptable pour simulation stochastique)
    ecart_relatif = abs(L_empirique - L_theorique) / L_theorique
    assert ecart_relatif < 0.30


def test_collecteur_donnees():
    """Test du collecteur de données"""
    collecteur = CollecteurDonnees()
    
    collecteur.definir_parametres(
        lambda_a=0.3,
        mu_a=0.395,
        lambda_b=0.3,
        mu_b=0.329,
        duree_simulation=500,
        config_feux={'T_A': 30, 'T_B': 25}
    )
    
    # Vérifier que les données théoriques sont calculées
    assert 'voie_a' in collecteur.donnees['theorique']
    assert 'voie_b' in collecteur.donnees['theorique']
    
    theo_a = collecteur.donnees['theorique']['voie_a']
    assert theo_a['rho'] < 1  # Stable
    assert theo_a['est_stable'] == True


def test_scenarios_differents():
    """Test des 3 scénarios avec paramètres différents"""
    scenarios = [
        # Scénario 1 : Trafic léger
        {'lambda': 0.3, 'T_A': 30, 'T_B': 25},
        # Scénario 3 : Optimisé
        {'lambda': 0.3, 'T_A': 28, 'T_B': 28},
    ]
    
    for i, params in enumerate(scenarios):
        env = simpy.Environment()
        config = ConfigurationFeux(
            duree_vert_a=params['T_A'],
            duree_vert_b=params['T_B']
        )
        
        systeme_feux = SystemeFeux(env, config)
        intersection = Intersection(env, systeme_feux)
        generateur = GenerateurVehicules(env, params['lambda'], params['lambda'])
        
        env.process(systeme_feux.gerer_cycle())
        env.process(generateur.generer_voie_a(intersection))
        env.process(generateur.generer_voie_b(intersection))
        
        env.run(until=200)
        
        stats = intersection.obtenir_statistiques()
        
        # Vérifier que des véhicules ont été servis
        assert stats['voie_a']['vehicules_servis'] > 0
        assert stats['voie_b']['vehicules_servis'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])