"""
GRAPHIQUES_COMPARATIFS.PY
Script standalone pour générer tous les graphiques
Responsable : Tasnim
Projet : Simulation Feux de Circulation
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11

def charger_scenario(nom_fichier):
    """Charge un fichier JSON"""
    with open(nom_fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

def creer_dossier_figures():
    """Crée le dossier figures s'il n'existe pas"""
    os.makedirs('figures', exist_ok=True)

def graphique_temps_attente(donnees, scenarios_labels):
    """Graphique 1 : Temps d'attente"""
    temps_a = [d['Wq_a_emp'] for d in donnees]
    temps_b = [d['Wq_b_emp'] for d in donnees]
    
    x = np.arange(len(scenarios_labels))
    largeur = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - largeur/2, temps_a, largeur, label='Voie A', 
                   color='#3498db', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + largeur/2, temps_b, largeur, label='Voie B', 
                   color='#e74c3c', edgecolor='black', linewidth=1.2)
    
    # Valeurs
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    ax.set_xlabel('Scénarios', fontsize=13, fontweight='bold')
    ax.set_ylabel('Temps d\'attente moyen (secondes)', fontsize=13, fontweight='bold')
    ax.set_title('Comparaison des Temps d\'Attente Moyens', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios_labels)
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('figures/comparaison_temps_attente.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique 1 créé : comparaison_temps_attente.png")
    plt.close()

def graphique_taux_utilisation(donnees, scenarios_labels):
    """Graphique 2 : Taux d'utilisation"""
    rho_a = [d['rho_a_theo'] for d in donnees]
    rho_b = [d['rho_b_theo'] for d in donnees]
    
    x = np.arange(len(scenarios_labels))
    largeur = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - largeur/2, rho_a, largeur, label='Voie A', 
                   color='#2ecc71', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + largeur/2, rho_b, largeur, label='Voie B', 
                   color='#ff7979', edgecolor='black', linewidth=1.2)
    
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2.5, 
               label='Seuil ρ=1', zorder=5)
    
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_xlabel('Scénarios', fontsize=13, fontweight='bold')
    ax.set_ylabel('Taux d\'utilisation (ρ)', fontsize=13, fontweight='bold')
    ax.set_title('Taux d\'Utilisation (ρ = λ/μ)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios_labels)
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('figures/comparaison_taux_utilisation.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique 2 créé : comparaison_taux_utilisation.png")
    plt.close()

def graphique_theorie_vs_simulation(donnees):
    """Graphique 3 : Validation"""
    categories = ['Voie A', 'Voie B']
    theorique = [donnees[0]['Wq_a_theo'], donnees[0]['Wq_b_theo']]
    empirique = [donnees[0]['Wq_a_emp'], donnees[0]['Wq_b_emp']]
    
    x = np.arange(len(categories))
    largeur = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 7))
    bars1 = ax.bar(x - largeur/2, theorique, largeur, 
                   label='Théorique', color='#9b59b6', 
                   alpha=0.8, edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + largeur/2, empirique, largeur, 
                   label='Simulation', color='#1abc9c', 
                   alpha=0.8, edgecolor='black', linewidth=1.2)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('W_q (secondes)', fontsize=13, fontweight='bold')
    ax.set_title('Validation : Théorie vs Simulation (Scénario 1)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('figures/theorie_vs_simulation.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique 3 créé : theorie_vs_simulation.png")
    plt.close()

def graphique_vehicules_servis(donnees, scenarios_labels):
    """Graphique 4 : Véhicules servis"""
    servis_a = [d['servis_a'] for d in donnees]
    servis_b = [d['servis_b'] for d in donnees]
    
    x = np.arange(len(scenarios_labels))
    largeur = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - largeur/2, servis_a, largeur, label='Voie A', 
                   color='#3498db', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x + largeur/2, servis_b, largeur, label='Voie B', 
                   color='#e74c3c', edgecolor='black', linewidth=1.2)
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    ax.set_xlabel('Scénarios', fontsize=13, fontweight='bold')
    ax.set_ylabel('Nombre de véhicules', fontsize=13, fontweight='bold')
    ax.set_title('Véhicules Servis par Scénario', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios_labels)
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig('figures/vehicules_servis.png', dpi=300, bbox_inches='tight')
    print("✅ Graphique 4 créé : vehicules_servis.png")
    plt.close()

def main():
    print("\n" + "="*60)
    print("🎨 GÉNÉRATION DES GRAPHIQUES COMPARATIFS")
    print("="*60 + "\n")
    
    # Créer dossier
    creer_dossier_figures()
    
    # Charger les scénarios
    print("📂 Chargement des données...")
    s1 = charger_scenario('../sarah_implementation/results/scenario1_trafic_leger.json')
    s2 = charger_scenario('../sarah_implementation/results/scenario2_asymetrique.json')
    s3 = charger_scenario('../sarah_implementation/results/scenario3_optimise.json')
    print("✅ Données chargées\n")
    
    # Extraire
    donnees = []
    for s, nom in [(s1, 'Scénario 1\nTrafic Léger'), 
                   (s2, 'Scénario 2\nAsymétrique'), 
                   (s3, 'Scénario 3\nOptimisé')]:
        donnees.append({
            'nom': nom,
            'rho_a_theo': s['theorique']['voie_a']['rho'],
            'rho_b_theo': s['theorique']['voie_b']['rho'],
            'Wq_a_theo': s['theorique']['voie_a']['W_q'],
            'Wq_b_theo': s['theorique']['voie_b']['W_q'],
            'Wq_a_emp': s['empirique']['voie_a']['temps_attente_moyen'],
            'Wq_b_emp': s['empirique']['voie_b']['temps_attente_moyen'],
            'servis_a': s['empirique']['voie_a']['vehicules_servis'],
            'servis_b': s['empirique']['voie_b']['vehicules_servis'],
        })
    
    scenarios_labels = [d['nom'] for d in donnees]
    
    # Créer les graphiques
    print("🎨 Création des graphiques...\n")
    graphique_temps_attente(donnees, scenarios_labels)
    graphique_taux_utilisation(donnees, scenarios_labels)
    graphique_theorie_vs_simulation(donnees)
    graphique_vehicules_servis(donnees, scenarios_labels)
    
    print("\n" + "="*60)
    print("🎉 TERMINÉ ! Tous les graphiques sont dans figures/")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
