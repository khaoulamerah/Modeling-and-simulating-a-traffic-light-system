"""
MAIN.PY - Point d'entrée principal de la simulation
Responsable : Sarah
Projet : Simulation de Feux de Circulation

Ce script permet de :
- Tester une simulation simple
- Exécuter automatiquement les 3 scénarios définis par Khaoula
- Générer les fichiers JSON nécessaires pour la visualisation de Tasnim
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
) -> CollecteurDonnees:
    """
    Exécute une simulation complète et retourne les résultats.
    
    Args:
        duree_simulation: Durée totale de la simulation (secondes)
        lambda_a/b: Taux d'arrivée des véhicules (véhicules/seconde)
        config_feux: Configuration personnalisée des feux
        nom_scenario: Nom du fichier JSON de sortie
        mode_silencieux: Masque les messages détaillés (utile pour les 3 scénarios)
    
    Returns:
        CollecteurDonnees contenant tous les résultats
    """
    
    if not mode_silencieux:
        print("\n" + "═" * 70)
        print("🚦 DÉMARRAGE DE LA SIMULATION")
        print("═" * 70)
        print(f"📏 Durée : {duree_simulation} secondes")
        print(f"🚗 Voie A : λ = {lambda_a} véh/s")
        print(f"🚙 Voie B : λ = {lambda_b} véh/s")
    
    # Configuration par défaut si aucune n'est fournie
    if config_feux is None:
        config_feux = ConfigurationFeux()
    
    # Calcul des taux de service effectifs
    mu_max = 1.0  # 1 véhicule par seconde quand le feu est vert
    mu_a = mu_max * config_feux.proportion_vert_a()
    mu_b = mu_max * config_feux.proportion_vert_b()
    
    rho_a = lambda_a / mu_a if mu_a > 0 else float('inf')
    rho_b = lambda_b / mu_b if mu_b > 0 else float('inf')
    
    if not mode_silencieux:
        print(f"\n📊 Analyse de stabilité :")
        print(f"   Voie A → μ = {mu_a:.3f} véh/s → ρ = {rho_a:.3f} {'✅ Stable' if rho_a < 1 else '❌ Instable'}")
        print(f"   Voie B → μ = {mu_b:.3f} véh/s → ρ = {rho_b:.3f} {'✅ Stable' if rho_b < 1 else '❌ Instable'}")
        if rho_a >= 1 or rho_b >= 1:
            print("   ⚠️  ATTENTION : Au moins une voie est instable → files infinies possibles !")
    
    if not mode_silencieux:
        print(f"\n🚀 Lancement de la simulation...\n")
    
    # Environnement SimPy
    env = simpy.Environment()
    
    # Composants
    systeme_feux = SystemeFeux(env, config_feux)
    intersection = Intersection(env, systeme_feux)
    generateur = GenerateurVehicules(env, lambda_a, lambda_b)
    
    # Processus
    env.process(systeme_feux.gerer_cycle())
    env.process(generateur.generer_voie_a(intersection))
    env.process(generateur.generer_voie_b(intersection))
    
    # Exécution
    env.run(until=duree_simulation)
    
    if not mode_silencieux:
        print(f"✅ Simulation terminée en {duree_simulation} secondes !\n")
    
    # Collecte des données
    collecteur = CollecteurDonnees()
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
    
    stats_inter = intersection.obtenir_statistiques()
    stats_gen = generateur.obtenir_statistiques()
    stats_feux = systeme_feux.obtenir_statistiques()
    
    collecteur.enregistrer_resultats(stats_inter, stats_gen, stats_feux)
    
    # Sauvegarde JSON pour Tasnim
    chemin_results = os.path.join('..', 'results')
    os.makedirs(chemin_results, exist_ok=True)
    fichier_json = os.path.join(chemin_results, f"{nom_scenario}.json")
    collecteur.sauvegarder(fichier_json)
    
    if not mode_silencieux:
        print("📊 RÉSUMÉ DES RÉSULTATS :")
        print("─" * 50)
        print(f"🚗 Voie A → {stats_inter['voie_a']['vehicules_servis']} véhicules servis | "
              f"Attente moyenne : {stats_inter['voie_a']['temps_attente_moyen']:.2f}s")
        print(f"🚙 Voie B → {stats_inter['voie_b']['vehicules_servis']} véhicules servis | "
              f"Attente moyenne : {stats_inter['voie_b']['temps_attente_moyen']:.2f}s")
        print("─" * 50)
        print(f"💾 Fichier sauvegardé : {fichier_json}")
    
    return collecteur


def executer_3_scenarios():
    """
    Exécute les 3 scénarios définis par Khaoula dans son rapport
    → Génère 3 fichiers JSON dans ../results/ pour Tasnim
    """
    print("\n" + "🎯 " * 30)
    print("     EXÉCUTION DES 3 SCÉNARIOS DE RÉFÉRENCE")
    print("🎯 " * 30 + "\n")
    
    scenarios = [
        {
            "nom": "scenario1_trafic_leger",
            "titre": "Scénario 1 : Trafic Léger",
            "lambda_a": 0.3,
            "lambda_b": 0.3,
            "T_A": 30,
            "T_B": 25,
            "T_pietons": 15
        },
        {
            "nom": "scenario2_asymetrique",
            "titre": "Scénario 2 : Asymétrique (dangereux)",
            "lambda_a": 0.4,
            "lambda_b": 0.4,
            "T_A": 40,
            "T_B": 20,
            "T_pietons": 15
        },
        {
            "nom": "scenario3_optimise",
            "titre": "Scénario 3 : Optimisé (équilibré)",
            "lambda_a": 0.3,
            "lambda_b": 0.3,
            "T_A": 28,
            "T_B": 28,
            "T_pietons": 14
        }
    ]
    
    for i, sc in enumerate(scenarios, 1):
        print(f"📌 {sc['titre']} (Scénario {i}/3)")
        config = ConfigurationFeux(
            duree_vert_a=sc["T_A"],
            duree_vert_b=sc["T_B"],
            duree_pietons=sc.get("T_pietons", 15)
        )
        executer_simulation(
            duree_simulation=600,  # 10 minutes de simulation pour des stats solides
            lambda_a=sc["lambda_a"],
            lambda_b=sc["lambda_b"],
            config_feux=config,
            nom_scenario=sc["nom"],
            mode_silencieux=False  # On veut voir les résultats
        )
        print()
    
    print("🎉" * 30)
    print("TOUS LES SCÉNARIOS SONT TERMINÉS !")
    print("3 fichiers JSON ont été générés dans ../results/")
    print("→ Tasnim peut maintenant lancer graphiques_comparatifs.py")
    print("🎉" * 30)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           🚦 SIMULATION DE FEUX DE CIRCULATION 🚦           ║
    ║                                                               ║
    ║        Responsable implémentation : Sarah                     ║
    ║        Modélisation mathématique : Khaoula                    ║
    ║        Visualisation & Analyse   : Tasnim                     ║
    ║                                                               ║
    ║        Université 08 Mai 1945 - Guelma                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print("\n📋 MENU PRINCIPAL")
    print("   1. Simulation simple (test rapide)")
    print("   2. Exécuter les 3 scénarios complets (recommandé)")
    print("   3. Quitter")
    
    choix = input("\n🔸 Votre choix (1/2/3) : ").strip()
    
    if choix == "1":
        print("\n🚀 Lancement d'une simulation de test...")
        executer_simulation(
            duree_simulation=300,
            lambda_a=0.3,
            lambda_b=0.3,
            nom_scenario="test_simple"
        )
    
    elif choix == "2":
        executer_3_scenarios()
    
    elif choix == "3":
        print("\n👋 Merci et à bientôt !")
    
    else:
        print("\n❌ Choix invalide. Au revoir !")
    
    print("\n✅ Programme terminé.\n")