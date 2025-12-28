"""
MAIN.PY - Point d'entrée de la simulation
Responsable : Sarah
Projet : Simulation de Feux de Circulation

⚠️ CE MODULE FAIT TOURNER LA SIMULATION
   La visualisation graphique = travail de Tasnim
"""

import simpy
import os
from feux import SystemeFeux, ConfigurationFeux
from vehicule import GenerateurVehicules
from intersection import Intersection
from statistiques import CollecteurDonnees


def executer_simulation(
    duree_simulation: float = 500.0,
    lambda_a: float = 0.3,
    lambda_b: float = 0.3,
    config_feux: ConfigurationFeux = None,
    nom_scenario: str = "simulation",
    mode_silencieux: bool = False
):
    """
    Exécute une simulation complète
    
    Args:
        duree_simulation: Durée en secondes
        lambda_a: Taux d'arrivée voie A (véh/s)
        lambda_b: Taux d'arrivée voie B (véh/s)
        config_feux: Configuration des feux
        nom_scenario: Nom pour le fichier de sortie
        mode_silencieux: Réduire les affichages console
        
    Returns:
        CollecteurDonnees avec les résultats
    """
    
    if not mode_silencieux:
        print("\n" + "=" * 70)
        print("🚦 SIMULATION DE FEUX DE CIRCULATION")
        print("=" * 70)
        print(f"Durée : {duree_simulation}s")
        print(f"Taux arrivée Voie A : {lambda_a} véh/s")
        print(f"Taux arrivée Voie B : {lambda_b} véh/s")
    
    # Configuration des feux
    if config_feux is None:
        config_feux = ConfigurationFeux()
    
    # Calculer taux de service
    mu_max = 1.0  # 1 véh/s quand feu vert
    mu_a = mu_max * config_feux.proportion_vert_a()
    mu_b = mu_max * config_feux.proportion_vert_b()
    
    # Vérifier stabilité
    rho_a = lambda_a / mu_a
    rho_b = lambda_b / mu_b
    
    if not mode_silencieux:
        print(f"\n📊 Paramètres :")
        print(f"  μ_A = {mu_a:.3f} véh/s  →  ρ_A = {rho_a:.3f} "
              f"({'✅ Stable' if rho_a < 1 else '❌ Instable'})")
        print(f"  μ_B = {mu_b:.3f} véh/s  →  ρ_B = {rho_b:.3f} "
              f"({'✅ Stable' if rho_b < 1 else '❌ Instable'})")
    
    if rho_a >= 1 or rho_b >= 1:
        print("\n⚠️  ATTENTION : Système instable (ρ ≥ 1) !")
    
    if not mode_silencieux:
        print(f"\n🚀 Démarrage simulation...\n")
    
    # ===== CRÉER L'ENVIRONNEMENT SIMPY =====
    env = simpy.Environment()
    
    # Créer les composants
    systeme_feux = SystemeFeux(env, config_feux)
    intersection = Intersection(env, systeme_feux)
    generateur = GenerateurVehicules(env, lambda_a, lambda_b)
    
    # Lancer les processus
    env.process(systeme_feux.gerer_cycle())
    env.process(generateur.generer_voie_a(intersection))
    env.process(generateur.generer_voie_b(intersection))
    
    # ===== EXÉCUTER =====
    env.run(until=duree_simulation)
    
    if not mode_silencieux:
        print(f"\n✅ Simulation terminée ! ({duree_simulation}s)\n")
    
    # ===== COLLECTER LES DONNÉES =====
    collecteur = CollecteurDonnees()
    
    # Paramètres
    collecteur.definir_parametres(
        lambda_a=lambda_a,
        mu_a=mu_a,
        lambda_b=lambda_b,
        mu_b=mu_b,
        duree_simulation=duree_simulation,
        config_feux={
            'T_A': config_feux.duree_vert_a,
            'T_B': config_feux.duree_vert_b,
            'T_jaune': config_feux.duree_jaune,
            'T_pietons': config_feux.duree_pietons,
            'T_cycle': config_feux.duree_cycle
        }
    )
    
    # Résultats empiriques
    stats_inter = intersection.obtenir_statistiques()
    stats_gen = generateur.obtenir_statistiques()
    stats_feux = systeme_feux.obtenir_statistiques()
    
    collecteur.enregistrer_resultats(stats_inter, stats_gen, stats_feux)
    
    # Sauvegarder JSON pour Tasnim
    os.makedirs('../results', exist_ok=True)
    fichier = f'../results/{nom_scenario}.json'
    collecteur.sauvegarder(fichier)
    
    # Afficher résumé simple
    if not mode_silencieux:
        print("\n📊 RÉSULTATS :")
        print("-" * 70)
        print(f"Voie A :")
        print(f"  Véhicules servis : {stats_inter['voie_a']['vehicules_servis']}")
        print(f"  Temps attente moyen : {stats_inter['voie_a']['temps_attente_moyen']:.2f}s")
        print(f"\nVoie B :")
        print(f"  Véhicules servis : {stats_inter['voie_b']['vehicules_servis']}")
        print(f"  Temps attente moyen : {stats_inter['voie_b']['temps_attente_moyen']:.2f}s")
        print("-" * 70)
    
    return collecteur


def executer_3_scenarios():
    """
    Exécute les 3 scénarios définis par Khaoula
    
    Génère 3 fichiers JSON que Tasnim va utiliser
    """
    
    print("\n" + "🎯 " * 25)
    print("EXÉCUTION DES 3 SCÉNARIOS")
    print("🎯 " * 25)
    
    # ===== SCÉNARIO 1 : TRAFIC LÉGER =====
    print("\n📌 SCÉNARIO 1 : Trafic Léger (λ=0.3, T_A=30s, T_B=25s)")
    config1 = ConfigurationFeux(duree_vert_a=30, duree_vert_b=25)
    executer_simulation(
        duree_simulation=500,
        lambda_a=0.3,
        lambda_b=0.3,
        config_feux=config1,
        nom_scenario="scenario1_trafic_leger",
        mode_silencieux=True
    )
    
    # ===== SCÉNARIO 2 : TRAFIC ASYMÉTRIQUE =====
    print("\n📌 SCÉNARIO 2 : Asymétrique (λ=0.4, T_A=40s, T_B=20s)")
    config2 = ConfigurationFeux(duree_vert_a=40, duree_vert_b=20)
    executer_simulation(
        duree_simulation=500,
        lambda_a=0.4,
        lambda_b=0.4,
        config_feux=config2,
        nom_scenario="scenario2_asymetrique",
        mode_silencieux=True
    )
    
    # ===== SCÉNARIO 3 : OPTIMISÉ =====
    print("\n📌 SCÉNARIO 3 : Optimisé (λ=0.3, T_A=28s, T_B=28s)")
    config3 = ConfigurationFeux(duree_vert_a=28, duree_vert_b=28, duree_pietons=14)
    executer_simulation(
        duree_simulation=500,
        lambda_a=0.3,
        lambda_b=0.3,
        config_feux=config3,
        nom_scenario="scenario3_optimise",
        mode_silencieux=True
    )
    
    print("\n" + "🎉 " * 25)
    print("TERMINÉ ! 3 fichiers JSON créés dans results/")
    print("→ Tasnim peut maintenant faire ses visualisations")
    print("🎉 " * 25)


if __name__ == "__main__":
    """Point d'entrée"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     🚦 SIMULATION DE FEUX DE CIRCULATION 🚦                  ║
    ║                                                               ║
    ║     Responsable implémentation : Sarah                       ║
    ║     Université : 08 Mai 1945 Guelma                          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📋 OPTIONS :")
    print("  1. Simulation simple (test)")
    print("  2. Exécuter les 3 scénarios complets")
    print("  3. Quitter")
    
    choix = input("\nVotre choix (1/2/3) : ")
    
    if choix == "1":
        executer_simulation(
            duree_simulation=200,
            lambda_a=0.3,
            lambda_b=0.3,
            nom_scenario="test_simple"
        )
    
    elif choix == "2":
        executer_3_scenarios()
    
    elif choix == "3":
        print("\n👋 Au revoir !")
    
    else:
        print("\n❌ Choix invalide")
    
    print("\n✅ Programme terminé\n")