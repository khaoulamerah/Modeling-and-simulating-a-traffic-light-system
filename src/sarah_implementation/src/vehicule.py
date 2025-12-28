"""
VEHICULE.PY - Génération des véhicules selon la loi de Poisson
Responsable : Sarah
Projet : Simulation de Feux de Circulation

Basé sur la modélisation de Khaoula :
- Arrivées selon processus de Poisson (λ = 0.3 véh/s)
- Temps inter-arrivée ~ Exponentielle(λ)
"""

import simpy
import random
import numpy as np
from dataclasses import dataclass
from typing import List
from enum import Enum


class Direction(Enum):
    """Direction du véhicule"""
    VOIE_A = "Voie A (Ouest → Est)"
    VOIE_B = "Voie B (Nord → Sud)"


@dataclass
class Vehicule:
    """
    Représente un véhicule dans la simulation
    
    Attributes:
        id: Identifiant unique du véhicule
        direction: Direction du véhicule (VOIE_A ou VOIE_B)
        temps_arrivee: Temps d'arrivée dans le système (secondes)
        temps_depart: Temps de départ du système (secondes)
        temps_attente: Temps passé en attente au feu rouge
    """
    id: int
    direction: Direction
    temps_arrivee: float
    temps_depart: float = None
    temps_attente: float = 0.0
    
    def calculer_temps_total(self) -> float:
        """Calcule le temps total dans le système"""
        if self.temps_depart is not None:
            return self.temps_depart - self.temps_arrivee
        return 0.0


class GenerateurVehicules:
    """
    Génère des véhicules selon un processus de Poisson
    
    Basé sur la modélisation mathématique (Khaoula) :
    - Loi de Poisson : P(N(t) = k) = (λt)^k × e^(-λt) / k!
    - Temps inter-arrivée ~ Exponentielle(λ)
    - E[T] = 1/λ
    """
    
    def __init__(self, env: simpy.Environment, lambda_a: float, lambda_b: float):
        """
        Initialise le générateur
        
        Args:
            env: Environnement SimPy
            lambda_a: Taux d'arrivée pour voie A (véhicules/seconde)
            lambda_b: Taux d'arrivée pour voie B (véhicules/seconde)
        """
        self.env = env
        self.lambda_a = lambda_a
        self.lambda_b = lambda_b
        self.compteur_a = 0
        self.compteur_b = 0
        self.vehicules_a: List[Vehicule] = []
        self.vehicules_b: List[Vehicule] = []
        
    def temps_inter_arrivee(self, lambda_param: float) -> float:
        """
        Génère un temps inter-arrivée selon loi Exponentielle
        
        Formule : T ~ Exp(λ)
        Méthode : Inverse transform sampling
        
        Args:
            lambda_param: Paramètre λ de la loi exponentielle
            
        Returns:
            Temps en secondes jusqu'à la prochaine arrivée
        """
        return random.expovariate(lambda_param)
    
    def generer_voie_a(self, intersection):
        """
        Processus de génération pour la Voie A
        
        Args:
            intersection: Objet Intersection pour gérer le passage
        """
        while True:
            # Attendre le temps inter-arrivée (Loi Exponentielle)
            temps_attente = self.temps_inter_arrivee(self.lambda_a)
            yield self.env.timeout(temps_attente)
            
            # Créer un nouveau véhicule
            self.compteur_a += 1
            vehicule = Vehicule(
                id=self.compteur_a,
                direction=Direction.VOIE_A,
                temps_arrivee=self.env.now
            )
            
            self.vehicules_a.append(vehicule)
            
            print(f"[{self.env.now:.2f}s] 🚗 Véhicule A-{vehicule.id} arrive sur Voie A")
            
            # Démarrer le processus de traversée
            self.env.process(intersection.traverser_voie_a(vehicule))
    
    def generer_voie_b(self, intersection):
        """
        Processus de génération pour la Voie B
        
        Args:
            intersection: Objet Intersection pour gérer le passage
        """
        while True:
            temps_attente = self.temps_inter_arrivee(self.lambda_b)
            yield self.env.timeout(temps_attente)
            
            self.compteur_b += 1
            vehicule = Vehicule(
                id=self.compteur_b,
                direction=Direction.VOIE_B,
                temps_arrivee=self.env.now
            )
            
            self.vehicules_b.append(vehicule)
            
            print(f"[{self.env.now:.2f}s] 🚙 Véhicule B-{vehicule.id} arrive sur Voie B")
            
            self.env.process(intersection.traverser_voie_b(vehicule))
    
    def obtenir_statistiques(self) -> dict:
        """
        Calcule les statistiques des arrivées
        
        Returns:
            Dictionnaire avec statistiques par voie
        """
        def calculer_stats(vehicules: List[Vehicule]) -> dict:
            if not vehicules:
                return {
                    'nombre_total': 0,
                    'temps_attente_moyen': 0,
                    'temps_attente_max': 0
                }
            
            temps_attente = [v.temps_attente for v in vehicules if v.temps_depart is not None]
            
            return {
                'nombre_total': len(vehicules),
                'nombre_servis': len(temps_attente),
                'temps_attente_moyen': np.mean(temps_attente) if temps_attente else 0,
                'temps_attente_max': np.max(temps_attente) if temps_attente else 0,
                'temps_attente_std': np.std(temps_attente) if temps_attente else 0
            }
        
        return {
            'voie_a': calculer_stats(self.vehicules_a),
            'voie_b': calculer_stats(self.vehicules_b)
        }


# Test unitaire du module
if __name__ == "__main__":
    print("🧪 Test du module vehicule.py")
    print("=" * 50)
    
    # Créer un environnement de test
    env = simpy.Environment()
    
    # Paramètres selon Khaoula : λ = 0.3 véh/s
    lambda_a = 0.3
    lambda_b = 0.3
    
    generateur = GenerateurVehicules(env, lambda_a, lambda_b)
    
    # Simuler quelques arrivées
    print(f"\nTest avec λ_A = {lambda_a}, λ_B = {lambda_b}")
    print(f"Temps moyen inter-arrivée attendu : {1/lambda_a:.2f} secondes\n")
    
    # Générer 5 véhicules pour test
    temps_inter = []
    for i in range(5):
        t = generateur.temps_inter_arrivee(lambda_a)
        temps_inter.append(t)
        print(f"Véhicule {i+1} : temps inter-arrivée = {t:.2f}s")
    
    print(f"\nMoyenne observée : {np.mean(temps_inter):.2f}s")
    print(f"Moyenne théorique : {1/lambda_a:.2f}s")
    print("\n✅ Module vehicule.py opérationnel !")