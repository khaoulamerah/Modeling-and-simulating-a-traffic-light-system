"""
STATISTIQUES.PY - Collecte des données brutes pour Tasnim
Responsable : Sarah
Projet : Simulation de Feux de Circulation

  CE MODULE COLLECTE SEULEMENT LES DONNÉES
   L'analyse et visualisation = travail de Tasnim
"""

import json
import numpy as np
from typing import Dict


class StatistiquesTheorique:
    """
    Calcule les indicateurs théoriques M/M/1
    
    Formules de Khaoula :
    - ρ = λ/μ (taux d'utilisation)
    - L = ρ/(1-ρ) (longueur moyenne)
    - W = 1/(μ-λ) (temps moyen dans système)
    - L_q = ρ²/(1-ρ) (longueur file d'attente)
    - W_q = ρ/(μ-λ) (temps moyen d'attente)
    """
    
    def __init__(self, lambda_: float, mu: float):
        self.lambda_ = lambda_
        self.mu = mu
    
    @property
    def rho(self) -> float:
        """Taux d'utilisation ρ = λ/μ"""
        if self.mu == 0:
            return float('inf')
        return self.lambda_ / self.mu
    
    @property
    def est_stable(self) -> bool:
        """Vérifie la condition de stabilité ρ < 1"""
        return self.rho < 1
    
    @property
    def L(self) -> float:
        """Nombre moyen de véhicules dans le système"""
        if not self.est_stable:
            return float('inf')
        return self.rho / (1 - self.rho)
    
    @property
    def W(self) -> float:
        """Temps moyen dans le système (secondes)"""
        if not self.est_stable:
            return float('inf')
        return 1 / (self.mu - self.lambda_)
    
    @property
    def L_q(self) -> float:
        """Nombre moyen en attente dans la file"""
        if not self.est_stable:
            return float('inf')
        return (self.rho ** 2) / (1 - self.rho)
    
    @property
    def W_q(self) -> float:
        """Temps moyen d'attente (secondes)"""
        if not self.est_stable:
            return float('inf')
        return self.rho / (self.mu - self.lambda_)
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour export JSON"""
        return {
            'lambda': self.lambda_,
            'mu': self.mu,
            'rho': self.rho,
            'est_stable': self.est_stable,
            'L': self.L if self.est_stable else None,
            'W': self.W if self.est_stable else None,
            'L_q': self.L_q if self.est_stable else None,
            'W_q': self.W_q if self.est_stable else None
        }


class CollecteurDonnees:
    """
    Collecte les données brutes de simulation
    
     PAS D'ANALYSE ICI - juste collecter et sauvegarder
       Tasnim va lire ces JSON pour faire ses graphiques
    """
    
    def __init__(self):
        """Initialise le collecteur"""
        self.donnees = {
            'parametres': {},
            'theorique': {},
            'empirique': {},
            'historique': {
                'longueurs_files': {'voie_a': [], 'voie_b': []},
                'changements_feux': []
            }
        }
    
    def definir_parametres(self, lambda_a: float, mu_a: float, 
                          lambda_b: float, mu_b: float,
                          duree_simulation: float,
                          config_feux: dict):
        """
        Enregistre les paramètres de simulation
        
        Args:
            lambda_a, mu_a: Paramètres voie A
            lambda_b, mu_b: Paramètres voie B
            duree_simulation: Durée totale
            config_feux: Configuration des durées de feux
        """
        self.donnees['parametres'] = {
            'lambda_a': lambda_a,
            'mu_a': mu_a,
            'lambda_b': lambda_b,
            'mu_b': mu_b,
            'duree_simulation': duree_simulation,
            'config_feux': config_feux
        }
        
        # Calculer les résultats théoriques
        theo_a = StatistiquesTheorique(lambda_a, mu_a)
        theo_b = StatistiquesTheorique(lambda_b, mu_b)
        
        self.donnees['theorique'] = {
            'voie_a': theo_a.to_dict(),
            'voie_b': theo_b.to_dict()
        }
    
    def enregistrer_resultats(self, stats_intersection: dict, 
                             stats_generateur: dict, 
                             stats_feux: dict):
        """
        Enregistre les résultats empiriques de la simulation
        
        Args:
            stats_intersection: Stats de l'intersection
            stats_generateur: Stats du générateur
            stats_feux: Stats du système de feux
        """
        self.donnees['empirique'] = {
            'voie_a': stats_intersection['voie_a'],
            'voie_b': stats_intersection['voie_b'],
            'generateur': stats_generateur,
            'feux': stats_feux
        }
    
    def sauvegarder(self, nom_fichier: str):
        """
        Sauvegarde toutes les données en JSON
        
        Ce fichier sera lu par Tasnim pour ses graphiques
        
        Args:
            nom_fichier: Chemin du fichier (ex: results/scenario1.json)
        """
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            json.dump(self.donnees, f, indent=2, ensure_ascii=False)
        
        print(f" Données sauvegardées : {nom_fichier}")
        print(f"   → Tasnim peut maintenant générer les graphiques")


# Test unitaire
if __name__ == "__main__":
    print(" Test du module statistiques.py")
    print("=" * 50)
    
    # Test calcul théorique
    theo = StatistiquesTheorique(0.3, 0.395)
    print(f"\nTest théorique : λ=0.3, μ=0.395")
    print(f"  ρ = {theo.rho:.3f}")
    print(f"  W_q = {theo.W_q:.2f}s")
    print(f"  Stable : {theo.est_stable}")
    
    # Test collecteur
    collecteur = CollecteurDonnees()
    collecteur.definir_parametres(
        lambda_a=0.3, mu_a=0.395,
        lambda_b=0.3, mu_b=0.329,
        duree_simulation=500,
        config_feux={'T_A': 30, 'T_B': 25}
    )
    
    # Simuler des résultats
    collecteur.enregistrer_resultats(
        stats_intersection={
            'voie_a': {'temps_attente_moyen': 8.5, 'vehicules_servis': 145},
            'voie_b': {'temps_attente_moyen': 32.0, 'vehicules_servis': 140}
        },
        stats_generateur={},
        stats_feux={}
    )
    
    # Sauvegarder
    collecteur.sauvegarder('../results/test.json')
    
    print("\n Module opérationnel !")