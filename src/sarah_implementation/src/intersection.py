"""
INTERSECTION.PY - Gestion du carrefour et des files d'attente
Responsable : Sarah
Projet : Simulation de Feux de Circulation

Implémente le modèle de file d'attente M/M/1 (Khaoula) :
- λ = taux d'arrivée (véh/s)
- μ = taux de service (véh/s)
- ρ = λ/μ (taux d'utilisation)
- Condition de stabilité : ρ < 1
"""

import simpy
from typing import List
from vehicule import Vehicule
from feux import SystemeFeux


class FileAttente:
    """
    Représente une file d'attente pour une voie
    
    Modèle M/M/1 selon la théorie (Khaoula) :
    - M : Arrivées Markoviennes (Poisson)
    - M : Service Markovien (Exponentiel)
    - 1 : Un seul serveur (une voie)
    """
    
    def __init__(self, nom: str):
        """
        Args:
            nom: Nom de la file (ex: "File Voie A")
        """
        self.nom = nom
        self.vehicules_en_attente: List[Vehicule] = []
        self.historique_longueur = []  # Pour calculer L (longueur moyenne)
        self.temps_attente_total = 0.0
        self.nombre_vehicules_servis = 0
    
    def ajouter_vehicule(self, vehicule: Vehicule, temps_actuel: float):
        """Ajoute un véhicule à la file"""
        self.vehicules_en_attente.append(vehicule)
        self.historique_longueur.append({
            'temps': temps_actuel,
            'longueur': len(self.vehicules_en_attente)
        })
    
    def retirer_vehicule(self) -> Vehicule:
        """Retire le premier véhicule de la file (FIFO)"""
        if self.vehicules_en_attente:
            return self.vehicules_en_attente.pop(0)
        return None
    
    def longueur(self) -> int:
        """Retourne le nombre de véhicules en attente"""
        return len(self.vehicules_en_attente)
    
    def est_vide(self) -> bool:
        """Vérifie si la file est vide"""
        return len(self.vehicules_en_attente) == 0
    
    def enregistrer_service(self, temps_attente: float):
        """Enregistre qu'un véhicule a été servi"""
        self.temps_attente_total += temps_attente
        self.nombre_vehicules_servis += 1
    
    def temps_attente_moyen(self) -> float:
        """
        Calcule W_q (temps moyen d'attente)
        
        Formule théorique : W_q = ρ / (μ - λ)
        """
        if self.nombre_vehicules_servis == 0:
            return 0.0
        return self.temps_attente_total / self.nombre_vehicules_servis


class Intersection:
    """
    Gère le carrefour complet avec ses deux voies
    
    Coordonne :
    - Les files d'attente (M/M/1)
    - Le système de feux
    - Le passage des véhicules
    """
    
    def __init__(self, env: simpy.Environment, systeme_feux: SystemeFeux):
        """
        Args:
            env: Environnement SimPy
            systeme_feux: Système de feux de circulation
        """
        self.env = env
        self.systeme_feux = systeme_feux
        
        # Files d'attente pour chaque voie
        self.file_a = FileAttente("File Voie A")
        self.file_b = FileAttente("File Voie B")
        
        # Ressources SimPy (1 serveur par voie)
        self.voie_a = simpy.Resource(env, capacity=1)
        self.voie_b = simpy.Resource(env, capacity=1)
        
        # Statistiques globales
        self.vehicules_total_a = 0
        self.vehicules_total_b = 0
    
    def traverser_voie_a(self, vehicule: Vehicule):
        """
        Processus de traversée pour un véhicule sur la Voie A
        
        Implémente la logique M/M/1 :
        1. Arrivée dans la file
        2. Attente que le feu soit vert
        3. Service (traversée)
        4. Départ
        """
        # 1. Arrivée : ajouter à la file
        self.file_a.ajouter_vehicule(vehicule, self.env.now)
        self.vehicules_total_a += 1
        
        print(f"  └─ File A : {self.file_a.longueur()} véhicule(s)")
        
        # 2. Attendre que le feu soit vert
        while not self.systeme_feux.peut_passer_voie_a():
            yield self.env.timeout(0.1)  # Vérifier toutes les 0.1s
        
        # 3. Demander la ressource (serveur)
        with self.voie_a.request() as req:
            yield req
            
            # Retirer de la file
            self.file_a.retirer_vehicule()
            
            # Calculer temps d'attente
            temps_attente = self.env.now - vehicule.temps_arrivee
            vehicule.temps_attente = temps_attente
            
            print(f"[{self.env.now:.2f}s] ✅ Véhicule A-{vehicule.id} traverse "
                  f"(attendu {temps_attente:.2f}s)")
            
            # Temps de traversée (instantané dans ce modèle)
            yield self.env.timeout(0.1)
            
            # 4. Départ
            vehicule.temps_depart = self.env.now
            self.file_a.enregistrer_service(temps_attente)
    
    def traverser_voie_b(self, vehicule: Vehicule):
        """
        Processus de traversée pour un véhicule sur la Voie B
        
        Même logique que traverser_voie_a
        """
        self.file_b.ajouter_vehicule(vehicule, self.env.now)
        self.vehicules_total_b += 1
        
        print(f"  └─ File B : {self.file_b.longueur()} véhicule(s)")
        
        while not self.systeme_feux.peut_passer_voie_b():
            yield self.env.timeout(0.1)
        
        with self.voie_b.request() as req:
            yield req
            
            self.file_b.retirer_vehicule()
            temps_attente = self.env.now - vehicule.temps_arrivee
            vehicule.temps_attente = temps_attente
            
            print(f"[{self.env.now:.2f}s] ✅ Véhicule B-{vehicule.id} traverse "
                  f"(attendu {temps_attente:.2f}s)")
            
            yield self.env.timeout(0.1)
            
            vehicule.temps_depart = self.env.now
            self.file_b.enregistrer_service(temps_attente)
    
    def obtenir_statistiques(self) -> dict:
        """
        Calcule les indicateurs de performance
        
        Retourne les valeurs empiriques à comparer avec la théorie :
        - L : longueur moyenne de file
        - W_q : temps moyen d'attente
        - Nombre de véhicules servis
        """
        return {
            'voie_a': {
                'vehicules_total': self.vehicules_total_a,
                'vehicules_servis': self.file_a.nombre_vehicules_servis,
                'temps_attente_moyen': self.file_a.temps_attente_moyen(),
                'longueur_file_actuelle': self.file_a.longueur()
            },
            'voie_b': {
                'vehicules_total': self.vehicules_total_b,
                'vehicules_servis': self.file_b.nombre_vehicules_servis,
                'temps_attente_moyen': self.file_b.temps_attente_moyen(),
                'longueur_file_actuelle': self.file_b.longueur()
            }
        }


# Test unitaire du module
if __name__ == "__main__":
    print(" Test du module intersection.py")
    print("=" * 50)
    
    from feux import SystemeFeux, ConfigurationFeux
    
    # Créer environnement
    env = simpy.Environment()
    
    # Créer système de feux
    config = ConfigurationFeux()
    systeme_feux = SystemeFeux(env, config)
    env.process(systeme_feux.gerer_cycle())
    
    # Créer intersection
    intersection = Intersection(env, systeme_feux)
    
    # Créer quelques véhicules de test
    def generer_test():
        """Génère quelques véhicules de test"""
        for i in range(3):
            v = Vehicule(i+1, "VOIE_A", env.now)
            print(f"[{env.now:.2f}s] 🚗 Test véhicule A-{i+1}")
            env.process(intersection.traverser_voie_a(v))
            yield env.timeout(5)  # 1 véhicule toutes les 5 secondes
    
    env.process(generer_test())
    
    # Simuler 50 secondes
    env.run(until=50)
    
    # Afficher statistiques
    stats = intersection.obtenir_statistiques()
    print(f"\n Statistiques Voie A :")
    print(f"  - Véhicules total : {stats['voie_a']['vehicules_total']}")
    print(f"  - Véhicules servis : {stats['voie_a']['vehicules_servis']}")
    print(f"  - Temps attente moyen : {stats['voie_a']['temps_attente_moyen']:.2f}s")
    
    print("\n Module intersection.py opérationnel !")