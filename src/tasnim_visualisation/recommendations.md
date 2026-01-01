# RECOMMANDATIONS PRATIQUES

**Projet :** Optimisation des Feux de Circulation  
**Auteur :** Tasnim  
**Date :** Décembre 2025

---

## 🎯 Objectif

Fournir des **recommandations concrètes et applicables** pour optimiser la gestion des feux de circulation selon différents niveaux de trafic.

---

## 📊 Synthèse des Résultats

| Configuration | ρ_A | ρ_B | W_q_A | W_q_B | Verdict |
|---------------|-----|-----|-------|-------|---------|
| Actuelle (30s/25s) | 0.76 | 0.91 | 8s | 31s | ⚠️ Déséquilibrée |
| Asymétrique (40s/20s) | 0.81 | 1.62 | 11s | 128s | ❌ Instable |
| **Optimisée (28s/28s)** | **0.80** | **0.80** | **13s** | **13s** | **✅ Idéale** |

---

## 🚦 RECOMMANDATION 1 : Trafic Léger (λ ≤ 0.3 véh/s)

### Configuration Recommandée

```
T_A (feu vert voie A)     = 28 secondes
T_B (feu vert voie B)     = 28 secondes
T_jaune                   = 3 secondes
T_piétons                 = 14 secondes
T_cycle total             = 76 secondes
```

### Performances Attendues

- **Taux d'utilisation** : ρ_A = ρ_B ≈ 0.80 (80%)
- **Temps d'attente** : W_q ≈ 13 secondes pour les deux voies
- **Équité** : Traitement identique des deux voies
- **Marge de sécurité** : 20% de capacité disponible

### Avantages

✅ **Équilibre parfait** entre les deux voies  
✅ **Temps d'attente acceptables** (<15 secondes)  
✅ **Stabilité garantie** (ρ < 0.85)  
✅ **Équité** pour tous les usagers  

### Quand l'appliquer ?

- Heures creuses (10h-16h)
- Week-ends hors périodes de pointe
- Zones résidentielles à trafic modéré

---

## 🚗 RECOMMANDATION 2 : Trafic Moyen (λ = 0.4 véh/s)

### Option A : Augmenter les Durées de Vert

```
T_A = 35 secondes
T_B = 35 secondes
T_jaune = 3 secondes
T_piétons = 12 secondes
T_cycle total = 88 secondes
```

**Résultats attendus :**
- ρ_A = ρ_B ≈ 0.84 (stable)
- W_q ≈ 18 secondes

### Option B : Réduire la Phase Piétons

```
T_A = 32 secondes
T_B = 32 secondes
T_jaune = 3 secondes
T_piétons = 10 secondes (minimum réglementaire)
T_cycle total = 80 secondes
```

**Résultats attendus :**
- ρ_A = ρ_B ≈ 0.82 (stable)
- W_q ≈ 16 secondes

### Quand l'appliquer ?

- Heures de pointe modérées (8h-9h, 17h-18h)
- Zones commerciales en journée
- Axes secondaires avec trafic régulier

---

## 🚙 RECOMMANDATION 3 : Trafic Intense (λ > 0.5 véh/s)

### ⚠️ Le modèle M/M/1 n'est plus adapté

Pour un trafic intense, le simple ajustement des durées ne suffit plus. Il faut :

### Solution 1 : Modèle M/M/c (Plusieurs Voies)

**Principe :** Créer **2 voies parallèles** sur chaque direction

- Chaque voie traite les véhicules indépendamment
- Doublement du taux de service : μ_effectif = 2μ
- Permet de gérer jusqu'à λ = 0.8 véh/s

**Exemple :**
- 2 voies pour la direction A
- 2 voies pour la direction B
- Feux synchronisés

### Solution 2 : Feux Adaptatifs

**Principe :** Ajuster dynamiquement T_A et T_B selon la longueur des files

```python
# Algorithme simplifié
if file_A > file_B + 5:
    T_A = 35 secondes  (favoriser A)
    T_B = 25 secondes
elif file_B > file_A + 5:
    T_A = 25 secondes
    T_B = 35 secondes  (favoriser B)
else:
    T_A = T_B = 30 secondes  (équilibre)
```

**Avantages :**
- S'adapte en temps réel au trafic
- Optimisation automatique
- Réduit les temps d'attente de 20-30%

### Solution 3 : Infrastructure Physique

- Ajouter des voies de circulation
- Créer des bretelles de contournement
- Installer des ronds-points (pour certains cas)

### Quand l'appliquer ?

- Heures de pointe intenses (7h-9h, 17h-19h)
- Axes principaux et voies rapides
- Centre-ville avec fort trafic

---

## 🛠️ RECOMMANDATION 4 : Mise en Œuvre Pratique

### Étape 1 : Mesurer le Trafic Réel

**Méthode :**
- Installer des capteurs de comptage (boucles magnétiques, caméras)
- Mesurer λ pendant 1 semaine complète
- Identifier les périodes de pointe

**Outils :**
- Capteurs infrarouges
- Caméras avec reconnaissance automatique
- Applications de comptage manuel

### Étape 2 : Calculer les Paramètres Optimaux

**Formules :**

```
μ_nécessaire = λ / 0.80  (pour maintenir ρ = 80%)

T_vert = (μ_nécessaire × T_cycle) / μ_max

Exemple :
λ = 0.3 véh/s
μ_nécessaire = 0.3 / 0.80 = 0.375 véh/s
T_cycle = 76s
μ_max = 1 véh/s (débit max quand vert)

T_vert = (0.375 × 76) / 1 = 28.5 ≈ 28 secondes
```

### Étape 3 : Phase de Test

- **Durée** : 2 semaines
- **Monitoring** : Mesurer W_q réel
- **Ajustements** : ±2 secondes si nécessaire
- **Validation** : Comparer avec les prévisions

### Étape 4 : Déploiement Final

- Fixer les paramètres validés
- Former les équipes de maintenance
- Documenter la configuration
- Prévoir des révisions semestrielles

---

## 📈 RECOMMANDATION 5 : Optimisation Continue

### Stratégie Multi-Périodes

**Principe :** Adapter les feux selon l'heure de la journée

| Période | Horaires | λ estimé | Configuration |
|---------|----------|----------|---------------|
| Nuit | 23h-6h | 0.1 | T_A = T_B = 20s |
| Heures creuses | 10h-16h | 0.3 | T_A = T_B = 28s |
| Pointe modérée | 8h-9h, 17h-18h | 0.4 | T_A = T_B = 35s |
| Pointe intense | 7h-8h, 18h-19h | 0.6 | Feux adaptatifs |

### Système de Monitoring

**Indicateurs à suivre en continu :**

1. **Longueur des files** : N_A(t), N_B(t)
2. **Temps d'attente réel** : W_q mesuré
3. **Taux d'utilisation** : ρ estimé
4. **Nombre de cycles manqués** : Véhicules qui attendent >2 cycles

**Alertes automatiques :**
- Si ρ > 0.90 → Alerte niveau 1 (surveillance renforcée)
- Si ρ > 0.95 → Alerte niveau 2 (ajustement immédiat)
- Si file > 15 véhicules → Alerte niveau 3 (intervention manuelle)

---

## 🎓 RECOMMANDATION 6 : Formation et Documentation

### Pour les Gestionnaires de Trafic

**Compétences nécessaires :**
- Comprendre les concepts M/M/1 (ρ, λ, μ)
- Interpréter les graphiques de performance
- Utiliser les outils de simulation

**Formation suggérée :**
- Module 1 : Théorie des files d'attente (4h)
- Module 2 : Utilisation du logiciel de simulation (4h)
- Module 3 : Cas pratiques et optimisation (4h)

### Documentation à Maintenir

1. **Manuel de configuration** : Procédures pour chaque scénario
2. **Journal des modifications** : Historique des ajustements
3. **Base de données de trafic** : Mesures λ par période
4. **Guide de dépannage** : Solutions aux problèmes courants

---

## ⚡ RECOMMANDATION 7 : Technologies Futures

### Court Terme (1-2 ans)

**Capteurs Intelligents**
- Détection automatique de λ en temps réel
- Ajustement dynamique des feux
- Priorité aux véhicules d'urgence

### Moyen Terme (3-5 ans)

**Intelligence Artificielle**
- Apprentissage des patterns de trafic
- Prédiction des périodes de pointe
- Optimisation multi-carrefours

**Intégration V2X (Vehicle-to-Everything)**
- Communication voiture-infrastructure
- Réservation de créneaux verts
- Optimisation globale du réseau

### Long Terme (>5 ans)

**Véhicules Autonomes**
- Coordination directe avec les feux
- Élimination des temps d'attente
- Fluidité maximale du trafic

---

## 📋 CHECKLIST D'OPTIMISATION

### Avant de Modifier les Feux

- [ ] Mesurer λ réel sur au moins 1 semaine
- [ ] Calculer μ_nécessaire = λ / 0.80
- [ ] Vérifier que ρ < 0.85 pour toutes les voies
- [ ] Simuler la nouvelle configuration
- [ ] Prévoir une phase de test (2 semaines)

### Pendant la Phase de Test

- [ ] Monitoring continu des temps d'attente
- [ ] Comptage des véhicules servis
- [ ] Recueil de retours usagers
- [ ] Ajustements progressifs (±2s)
- [ ] Comparaison avec les prévisions théoriques

### Après Déploiement

- [ ] Documentation de la configuration finale
- [ ] Formation des équipes
- [ ] Planification des révisions (tous les 6 mois)
- [ ] Mise en place d'alertes automatiques
- [ ] Archivage des données pour analyses futures

---

## 🎯 Tableau de Décision Rapide

| Situation | λ mesuré | Action Recommandée |
|-----------|----------|-------------------|
| Trafic très faible | <0.2 | T_A = T_B = 20s |
| Trafic léger | 0.2-0.3 | **T_A = T_B = 28s** ✅ |
| Trafic moyen | 0.3-0.4 | T_A = T_B = 35s |
| Trafic élevé | 0.4-0.5 | Feux adaptatifs OU réduire T_piétons |
| Trafic saturé | >0.5 | Modèle M/M/c OU ajouter des voies |

---

## 💡 Conseils d'Expert

### Principe #1 : Toujours Vérifier la Stabilité

**Avant tout ajustement**, calculer :
```
ρ = λ / μ

Si ρ ≥ 1 → ⚠️ Configuration INTERDITE
Si ρ ≥ 0.95 → ⚠️ Risque élevé de congestion
Si 0.85 ≤ ρ < 0.95 → ⚠️ Surveillance requise
Si ρ < 0.85 → ✅ Configuration acceptable
```

### Principe #2 : Équilibrer les Voies

Viser **ρ_A ≈ ρ_B** pour une équité optimale :
- Évite la frustration des usagers d'une voie
- Optimise l'utilisation globale du carrefour
- Simplifie la gestion et le monitoring

### Principe #3 : Marge de Sécurité

Toujours prévoir **15-20% de capacité de réserve** :
- Absorbe les variations de trafic
- Compense les incidents (pannes, accidents)
- Gère les événements exceptionnels

---

## 📞 Contacts et Ressources

### Support Technique
- **Équipe de simulation** : sarah@simulation.dz
- **Modélisation** : khaoula@modelisation.dz
- **Analyse** : tasnim@analyse.dz

### Ressources en Ligne
- Documentation SimPy : https://simpy.readthedocs.io
- Théorie des files : https://queue-theory.org
- Standards de signalisation : AFNOR NF P99-200

---

## ✅ Conclusion

Ces recommandations permettent de :

✅ **Optimiser** les temps d'attente selon le niveau de trafic  
✅ **Garantir** la stabilité du système (ρ < 0.85)  
✅ **Équilibrer** les charges entre les voies  
✅ **Adapter** la configuration aux besoins réels  
✅ **Anticiper** l'évolution future du trafic  

**Recommandation principale :** Pour un trafic léger (λ = 0.3 véh/s), adopter la configuration **T_A = T_B = 28 secondes** qui offre le meilleur compromis entre efficacité, équité et stabilité.

---

**Document rédigé par Tasnim**  
**Université 08 Mai 1945 Guelma**  
**Module : Modélisation et Simulation**  
**Décembre 2024**
