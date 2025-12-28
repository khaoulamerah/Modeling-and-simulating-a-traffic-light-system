# 🚦 Simulation de Feux de Circulation

Projet de Modélisation et Simulation - Université 08 Mai 1945 Guelma

## 👥 Équipe
- **Khaoula** : Modélisation mathématique
- **Sarah** : Implémentation Python
- **Tasnim** : Visualisation et analyse

## 📦 Installation
```bash
# Cloner le projet
cd sarah_implementation

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer dépendances
pip install -r requirements.txt
```

## 🚀 Utilisation
```bash
# Lancer la simulation
python src/main.py
```

## 📊 Structure

- `src/` : Code source
  - `main.py` : Point d'entrée
  - `vehicule.py` : Génération véhicules
  - `feux.py` : Système de feux
  - `intersection.py` : Gestion carrefour
  - `statistiques.py` : Analyse résultats
- `tests/` : Tests unitaires
- `results/` : Résultats JSON

## 📖 Modèle Mathématique

Voir `khaoula_modelisation/modelisation.ipynb`

- Processus de Poisson pour les arrivées
- Automate fini à 5 états pour les feux
- Files d'attente M/M/1