"""
FEUX.PY - Système de feux de circulation
Responsable : Sarah
Projet : Simulation de Feux de Circulation

Basé sur la modélisation de Khaoula :
- Automate fini à 5 états (S1 → S2 → S3 → S4 → S5 → S1)
- Chaîne de Markov déterministe
- Cycle total : 76 secondes
"""

import simpy
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CouleurFeu(Enum):
    """États possibles d'un feu de circulation"""
    VERT = "🟢"
    JAUNE = "🟡"
    ROUGE = "🔴"


class EtatSysteme(Enum):
    """
    États du système selon l'automate fini (Khaoula)
    
    Cycle : S1 → S2 → S3 → S4 → S5 → S1
    """
    S1 = "Voie A Vert"      # A=Vert, B=Rouge, Piétons=Rouge (30s)
    S2 = "Voie A Jaune"     # A=Jaune, B=Rouge, Piétons=Rouge (3s)
    S3 = "Voie B Vert"      # A=Rouge, B=Vert, Piétons=Rouge (25s)
    S4 = "Voie B Jaune"     # A=Rouge, B=Jaune, Piétons=Rouge (3s)
    S5 = "Piétons"          # A=Rouge, B=Rouge, Piétons=Vert (15s)


@dataclass
class ConfigurationFeux:
    """
    Configuration des durées des feux (en secondes)
    
    Valeurs par défaut selon la modélisation mathématique :
    - T_A = 30s (voie A verte)
    - T_B = 25s (voie B verte)
    - T_jaune = 3s (transition)
    - T_piétons = 15s (phase piétons)
    - T_cycle = 76s (cycle total)
    """
    duree_vert_a: float = 30.0      # T_A
    duree_vert_b: float = 25.0      # T_B
    duree_jaune: float = 3.0        # T_jaune
    duree_pietons: float = 15.0     # T_piétons
    
    @property
    def duree_cycle(self) -> float:
        """Calcule la durée totale du cycle"""
        return (self.duree_vert_a + self.duree_jaune + 
                self.duree_vert_b + self.duree_jaune + 
                self.duree_pietons)
    
    def proportion_vert_a(self) -> float:
        """Calcule α_A = T_A / T_cycle (proportion temps vert voie A)"""
        return self.duree_vert_a / self.duree_cycle
    
    def proportion_vert_b(self) -> float:
        """Calcule α_B = T_B / T_cycle (proportion temps vert voie B)"""
        return self.duree_vert_b / self.duree_cycle


class Feu:
    """
    Représente un feu de circulation individuel
    """
    
    def __init__(self, nom: str, couleur_initiale: CouleurFeu = CouleurFeu.ROUGE):
        """
        Args:
            nom: Nom du feu (ex: "Feu Voie A")
            couleur_initiale: Couleur au démarrage
        """
        self.nom = nom
        self.couleur = couleur_initiale
        self.historique = []  # Pour l'analyse
    
    def changer_couleur(self, nouvelle_couleur: CouleurFeu, temps: float):
        """Change la couleur du feu et enregistre l'événement"""
        self.couleur = nouvelle_couleur
        self.historique.append({
            'temps': temps,
            'couleur': nouvelle_couleur
        })
    
    def est_vert(self) -> bool:
        """Vérifie si le feu est vert"""
        return self.couleur == CouleurFeu.VERT
    
    def est_rouge(self) -> bool:
        """Vérifie si le feu est rouge"""
        return self.couleur == CouleurFeu.ROUGE


class SystemeFeux:
    """
    Gère le système complet de feux de circulation
    
    Implémente l'automate fini à 5 états selon la modélisation de Khaoula :
    - Fonction de transition δ : E × Σ → E
    - Transitions déterministes basées sur le temps
    """
    
    def __init__(self, env: simpy.Environment, config: Optional[ConfigurationFeux] = None):
        """
        Args:
            env: Environnement SimPy
            config: Configuration des durées (ou valeurs par défaut)
        """
        self.env = env
        self.config = config or ConfigurationFeux()
        
        # Créer les feux individuels
        self.feu_a = Feu("Feu Voie A", CouleurFeu.VERT)  # État initial S1
        self.feu_b = Feu("Feu Voie B", CouleurFeu.ROUGE)
        self.feu_pietons = Feu("Feu Piétons", CouleurFeu.ROUGE)
        
        # État actuel du système
        self.etat_actuel = EtatSysteme.S1
        self.nombre_cycles = 0
        
        # Statistiques
        self.historique_etats = []
    
    def obtenir_etat(self) -> tuple:
        """
        Retourne l'état actuel des 3 feux
        
        Returns:
            (couleur_feu_a, couleur_feu_b, couleur_pietons)
        """
        return (self.feu_a.couleur, self.feu_b.couleur, self.feu_pietons.couleur)
    
    def peut_passer_voie_a(self) -> bool:
        """Vérifie si les véhicules peuvent passer sur la voie A"""
        return self.feu_a.est_vert()
    
    def peut_passer_voie_b(self) -> bool:
        """Vérifie si les véhicules peuvent passer sur la voie B"""
        return self.feu_b.est_vert()
    
    def transition_etat(self, nouvel_etat: EtatSysteme):
        """
        Effectue une transition vers un nouvel état
        
        Correspond à la fonction δ de l'automate fini
        """
        self.etat_actuel = nouvel_etat
        self.historique_etats.append({
            'temps': self.env.now,
            'etat': nouvel_etat
        })
    
    def gerer_cycle(self):
        """
        Processus principal : gère le cycle complet des feux
        
        Implémente l'automate fini :
        S1 --T_A--> S2 --T_jaune--> S3 --T_B--> S4 --T_jaune--> S5 --T_piétons--> S1
        """
        while True:
            # ===== ÉTAT S1 : Voie A Verte =====
            self.transition_etat(EtatSysteme.S1)
            self.feu_a.changer_couleur(CouleurFeu.VERT, self.env.now)
            self.feu_b.changer_couleur(CouleurFeu.ROUGE, self.env.now)
            self.feu_pietons.changer_couleur(CouleurFeu.ROUGE, self.env.now)
            
            print(f"\n[{self.env.now:.2f}s] 🔄 État S1 : {CouleurFeu.VERT.value} Voie A | {CouleurFeu.ROUGE.value} Voie B | {CouleurFeu.ROUGE.value} Piétons")
            
            yield self.env.timeout(self.config.duree_vert_a)
            
            # ===== ÉTAT S2 : Voie A Jaune =====
            self.transition_etat(EtatSysteme.S2)
            self.feu_a.changer_couleur(CouleurFeu.JAUNE, self.env.now)
            
            print(f"[{self.env.now:.2f}s] 🔄 État S2 : {CouleurFeu.JAUNE.value} Voie A | {CouleurFeu.ROUGE.value} Voie B")
            
            yield self.env.timeout(self.config.duree_jaune)
            
            # ===== ÉTAT S3 : Voie B Verte =====
            self.transition_etat(EtatSysteme.S3)
            self.feu_a.changer_couleur(CouleurFeu.ROUGE, self.env.now)
            self.feu_b.changer_couleur(CouleurFeu.VERT, self.env.now)
            
            print(f"[{self.env.now:.2f}s] 🔄 État S3 : {CouleurFeu.ROUGE.value} Voie A | {CouleurFeu.VERT.value} Voie B | {CouleurFeu.ROUGE.value} Piétons")
            
            yield self.env.timeout(self.config.duree_vert_b)
            
            # ===== ÉTAT S4 : Voie B Jaune =====
            self.transition_etat(EtatSysteme.S4)
            self.feu_b.changer_couleur(CouleurFeu.JAUNE, self.env.now)
            
            print(f"[{self.env.now:.2f}s] 🔄 État S4 : {CouleurFeu.ROUGE.value} Voie A | {CouleurFeu.JAUNE.value} Voie B")
            
            yield self.env.timeout(self.config.duree_jaune)
            
            # ===== ÉTAT S5 : Phase Piétons =====
            self.transition_etat(EtatSysteme.S5)
            self.feu_b.changer_couleur(CouleurFeu.ROUGE, self.env.now)
            self.feu_pietons.changer_couleur(CouleurFeu.VERT, self.env.now)
            
            print(f"[{self.env.now:.2f}s] 🔄 État S5 : {CouleurFeu.ROUGE.value} Voie A | {CouleurFeu.ROUGE.value} Voie B | {CouleurFeu.VERT.value} Piétons")
            
            yield self.env.timeout(self.config.duree_pietons)
            
            # Fin du cycle
            self.nombre_cycles += 1
            print(f"[{self.env.now:.2f}s] ✅ Cycle {self.nombre_cycles} terminé")
    
    def obtenir_statistiques(self) -> dict:
        """
        Calcule les statistiques du système de feux
        
        Returns:
            Dictionnaire avec statistiques selon la théorie (Khaoula)
        """
        return {
            'nombre_cycles': self.nombre_cycles,
            'duree_cycle': self.config.duree_cycle,
            'proportion_vert_a': self.config.proportion_vert_a(),
            'proportion_vert_b': self.config.proportion_vert_b(),
            'temps_simulation': self.env.now
        }


# Test unitaire du module
if __name__ == "__main__":
    print("🧪 Test du module feux.py")
    print("=" * 50)
    
    # Créer environnement de test
    env = simpy.Environment()
    
    # Configuration par défaut (selon Khaoula)
    config = ConfigurationFeux()
    print(f"\nConfiguration des feux :")
    print(f"  - Durée vert Voie A : {config.duree_vert_a}s")
    print(f"  - Durée vert Voie B : {config.duree_vert_b}s")
    print(f"  - Durée jaune : {config.duree_jaune}s")
    print(f"  - Durée piétons : {config.duree_pietons}s")
    print(f"  - Durée cycle : {config.duree_cycle}s")
    print(f"  - Proportion vert A : {config.proportion_vert_a():.2%}")
    print(f"  - Proportion vert B : {config.proportion_vert_b():.2%}")
    
    # Créer système de feux
    systeme = SystemeFeux(env, config)
    
    # Lancer le cycle
    env.process(systeme.gerer_cycle())
    
    # Simuler 2 cycles complets
    duree_test = 2 * config.duree_cycle
    env.run(until=duree_test)
    
    # Afficher statistiques
    stats = systeme.obtenir_statistiques()
    print(f"\n📊 Statistiques après {duree_test}s :")
    print(f"  - Cycles complétés : {stats['nombre_cycles']}")
    print(f"  - Temps de simulation : {stats['temps_simulation']:.2f}s")
    
    print("\n✅ Module feux.py opérationnel !")