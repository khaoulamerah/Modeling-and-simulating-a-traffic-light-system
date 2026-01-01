"""
FEUX.PY - Traffic Light System
Responsible: Sarah
Project: Traffic Light Simulation

Based on Khaoula's modeling:
- Finite automaton with 5 states (S1 → S2 → S3 → S4 → S5 → S1)
- Deterministic Markov Chain
- Total cycle: 76 seconds
"""

import simpy
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class CouleurFeu(Enum):
    """Possible states of a traffic light"""
    VERT = "🟢"
    JAUNE = "🟡"
    ROUGE = "🔴"


class EtatSysteme(Enum):
    """
    System states according to the finite automaton (Khaoula)
    
    Cycle: S1 → S2 → S3 → S4 → S5 → S1
    """
    S1 = "Lane A Green"      # A=Green, B=Red, Pedestrians=Red (30s)
    S2 = "Lane A Yellow"     # A=Yellow, B=Red, Pedestrians=Red (3s)
    S3 = "Lane B Green"      # A=Red, B=Green, Pedestrians=Red (25s)
    S4 = "Lane B Yellow"     # A=Red, B=Yellow, Pedestrians=Red (3s)
    S5 = "Pedestrians"       # A=Red, B=Red, Pedestrians=Green (15s)


@dataclass
class ConfigurationFeux:
    """
    Configuration of traffic light durations (in seconds)
    
    Default values according to the mathematical modeling:
    - T_A = 30s (Lane A green)
    - T_B = 25s (Lane B green)
    - T_yellow = 3s (transition)
    - T_pedestrians = 15s (pedestrian phase)
    - T_cycle = 76s (total cycle)
    """
    duree_vert_a: float = 30.0      # T_A
    duree_vert_b: float = 25.0      # T_B
    duree_jaune: float = 3.0        # T_yellow
    duree_pietons: float = 15.0     # T_pedestrians
    
    @property
    def duree_cycle(self) -> float:
        """Calculates the total cycle duration"""
        return (self.duree_vert_a + self.duree_jaune + 
                self.duree_vert_b + self.duree_jaune + 
                self.duree_pietons)
    
    def proportion_vert_a(self) -> float:
        """Calculates α_A = T_A / T_cycle (proportion of green time for Lane A)"""
        return self.duree_vert_a / self.duree_cycle
    
    def proportion_vert_b(self) -> float:
        """Calculates α_B = T_B / T_cycle (proportion of green time for Lane B)"""
        return self.duree_vert_b / self.duree_cycle


class SystemeFeux:
    """
    Manages the traffic light system
    
    Implements the finite automaton and cycle management
    """
    
    def __init__(self, env: simpy.Environment, config: ConfigurationFeux):
        """
        Args:
            env: SimPy environment
            config: Light configuration
        """
        self.env = env
        self.config = config
        self.etat_courant = EtatSysteme.S1  # Initial state
        self.nombre_cycles = 0
    
    def peut_passer_voie_a(self) -> bool:
        """
        Returns True if vehicles on Lane A can pass (green or yellow)
        """
        return self.etat_courant in [EtatSysteme.S1, EtatSysteme.S2]

    def peut_passer_voie_b(self) -> bool:
        """
        Returns True if vehicles on Lane B can pass (green or yellow)
        """
        return self.etat_courant in [EtatSysteme.S3, EtatSysteme.S4]
    
    def gerer_cycle(self):
        """Manages the infinite cycle of lights"""
        while True:
            # S1: Lane A Green
            self.etat_courant = EtatSysteme.S1
            print(f"[{self.env.now:.2f}s] 🟢 Lane A Green (B Red, Pedestrians Red)")
            yield self.env.timeout(self.config.duree_vert_a)
            
            # S2: Lane A Yellow
            self.etat_courant = EtatSysteme.S2
            print(f"[{self.env.now:.2f}s] 🟡 Lane A Yellow (B Red, Pedestrians Red)")
            yield self.env.timeout(self.config.duree_jaune)
            
            # S3: Lane B Green
            self.etat_courant = EtatSysteme.S3
            print(f"[{self.env.now:.2f}s] 🟢 Lane B Green (A Red, Pedestrians Red)")
            yield self.env.timeout(self.config.duree_vert_b)
            
            # S4: Lane B Yellow
            self.etat_courant = EtatSysteme.S4
            print(f"[{self.env.now:.2f}s] 🟡 Lane B Yellow (A Red, Pedestrians Red)")
            yield self.env.timeout(self.config.duree_jaune)
            
            # S5: Pedestrians
            self.etat_courant = EtatSysteme.S5
            print(f"[{self.env.now:.2f}s] 🚶 Pedestrians Green (A Red, B Red)")
            yield self.env.timeout(self.config.duree_pietons)
            
            self.nombre_cycles += 1
            print(f"[{self.env.now:.2f}s] ✅ Cycle {self.nombre_cycles} completed")
    
    def obtenir_statistiques(self) -> dict:
        """
        Calculates the statistics of the traffic light system
        
        Returns:
            Dictionary with statistics according to the theory (Khaoula)
        """
        return {
            'nombre_cycles': self.nombre_cycles,
            'duree_cycle': self.config.duree_cycle,
            'proportion_vert_a': self.config.proportion_vert_a(),
            'proportion_vert_b': self.config.proportion_vert_b(),
            'temps_simulation': self.env.now
        }

# Unit test of the module
if __name__ == "__main__":
    print("🧪 Test of the module feux.py")
    print("=" * 50)
    
    # Create test environment
    env = simpy.Environment()
    
    # Default configuration (according to Khaoula)
    config = ConfigurationFeux()
    print(f"\nTraffic light configuration:")
    print(f"  - Green duration Lane A: {config.duree_vert_a}s")
    print(f"  - Green duration Lane B: {config.duree_vert_b}s")
    print(f"  - Yellow duration: {config.duree_jaune}s")
    print(f"  - Pedestrians duration: {config.duree_pietons}s")
    print(f"  - Cycle duration: {config.duree_cycle}s")
    print(f"  - Proportion green A: {config.proportion_vert_a():.2%}")
    print(f"  - Proportion green B: {config.proportion_vert_b():.2%}")
    
    # Create traffic light system
    systeme = SystemeFeux(env, config)
    
    # Start the cycle
    env.process(systeme.gerer_cycle())
    
    # Simulate 2 complete cycles
    duree_test = 2 * config.duree_cycle
    env.run(until=duree_test)
    
    # Display statistics
    stats = systeme.obtenir_statistiques()
    print(f"\n📊 Statistics after {duree_test}s:")
    print(f"  - Completed cycles: {stats['nombre_cycles']}")
    print(f"  - Simulation time: {stats['temps_simulation']:.2f}s")
    
    print("\n✅ Module feux.py operational!")