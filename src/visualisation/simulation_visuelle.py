"""
SIMULATION_VISUELLE.PY - Version finale corrigée (Fenêtres uniformes)
Projet : Simulation de Feux de Circulation
CORRECTIONS FINALES :
✅ Les deux fenêtres ont EXACTEMENT la même taille (900x650)
✅ Écran de sélection + simulation : même dimensions, centrées
✅ Files d'attente un peu plus éloignées de l'intersection
✅ Voie A + feu descendus, sans collision
✅ ÉCHAP pour quitter
"""

import pygame
import sys
import threading
import time
from queue import Queue
from dataclasses import dataclass
from typing import List
import os
import random

# Import simulation
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sarah_implementation', 'src'))
import simpy
from feux import SystemeFeux, ConfigurationFeux, CouleurFeu
from vehicule import GenerateurVehicules, Vehicule, Direction
from intersection import Intersection
from statistiques import CollecteurDonnees

# ========== CONFIGURATION FENÊTRE ==========
FENETRE_LARGEUR = 900
FENETRE_HAUTEUR = 650

FOND = (240, 242, 245)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ASPHALTE = (45, 52, 58)
LIGNE_JAUNE = (255, 215, 0)
BLEU = (52, 152, 219)
ORANGE = (255, 127, 80)
VERT_STATS = (46, 213, 115)

# Échelle pour la simulation (adaptée à 900x650)
LARGEUR_ROUTE = 120
TAILLE_VOITURE = int(80 * 1.3)      # ~104px
ESPACEMENT_VOITURE = int(95 * 1.3)  # ~124px
TAILLE_FEU = int(70 * 1.3)          # ~91px

# Déplacement Voie A vers le bas
OFFSET_VOIE_A_Y = 60

# Distance de départ des files (un peu plus loin)
DISTANCE_DEPART_FILE = 230  # au lieu de 200

# ========== CHARGEMENT DES IMAGES ==========
def charger_images():
    assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    images = {}
   
    for i in range(1, 6):
        try:
            img = pygame.image.load(os.path.join(assets_path, f'car{i}.png'))
            img = pygame.transform.scale(img, (TAILLE_VOITURE, int(TAILLE_VOITURE * 1.2)))
            images[f'car{i}'] = img
        except Exception as e:
            print(f"⚠️ Impossible de charger car{i}.png: {e}")
            images[f'car{i}'] = None
   
    for couleur in ['green', 'orange', 'red']:
        try:
            img = pygame.image.load(os.path.join(assets_path, f'{couleur}.png'))
            img = pygame.transform.scale(img, (TAILLE_FEU, TAILLE_FEU))
            images[couleur] = img
        except Exception as e:
            print(f"⚠️ Impossible de charger {couleur}.png: {e}")
            images[couleur] = None
   
    return images

def dessiner_voiture_fallback(surface, x, y, largeur, hauteur, couleur):
    pygame.draw.rect(surface, couleur, (x, y, largeur, hauteur), border_radius=10)
    pygame.draw.rect(surface, NOIR, (x, y, largeur, hauteur), 3, border_radius=10)

# ========== CLASSES ==========
@dataclass
class VoitureGraphique:
    vehicule: Vehicule
    x: float
    y: float
    image: pygame.Surface
    couleur_fallback: tuple
    direction: str
    en_attente: bool = True

class CarrefourGraphique:
    def __init__(self, largeur, hauteur, images):
        self.largeur = largeur
        self.hauteur = hauteur
        self.images = images
       
        self.centre_x = largeur // 2
        self.centre_y = hauteur // 2 + OFFSET_VOIE_A_Y
       
        self.voitures_a: List[VoitureGraphique] = []
        self.voitures_b: List[VoitureGraphique] = []
       
        self.couleur_feu_a = 'red'
        self.couleur_feu_b = 'red'
       
        self.pos_feu_a = (self.centre_x - 220, self.centre_y + LARGEUR_ROUTE // 2 + 30)
        self.pos_feu_b = (self.centre_x + LARGEUR_ROUTE // 2 + 30, self.centre_y - 220)
       
        self.stats = {
            'voie_a_attente': 0, 'voie_b_attente': 0,
            'voie_a_servis': 0, 'voie_b_servis': 0,
            'temps_attente_a': 0, 'temps_attente_b': 0,
            'total_vehicules': 0, 'debit_a': 0, 'debit_b': 0,
            'historique_a': [], 'historique_b': []
        }
        self.dernier_temps_stats = 0
   
    def dessiner_routes(self, surface):
        # Horizontale (Voie A)
        pygame.draw.rect(surface, ASPHALTE,
                         (0, self.centre_y - LARGEUR_ROUTE//2, self.largeur, LARGEUR_ROUTE))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                         (0, self.centre_y - LARGEUR_ROUTE//2 - 4, self.largeur, 5))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                         (0, self.centre_y + LARGEUR_ROUTE//2, self.largeur, 5))
        for i in range(0, self.largeur, 60):
            if not (self.centre_x - LARGEUR_ROUTE//2 < i < self.centre_x + LARGEUR_ROUTE//2):
                pygame.draw.rect(surface, BLANC, (i, self.centre_y - 4, 35, 8))
       
        # Verticale (Voie B)
        centre_y_b = self.hauteur // 2
        pygame.draw.rect(surface, ASPHALTE,
                         (self.centre_x - LARGEUR_ROUTE//2, 0, LARGEUR_ROUTE, self.hauteur))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                         (self.centre_x - LARGEUR_ROUTE//2 - 4, 0, 5, self.hauteur))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                         (self.centre_x + LARGEUR_ROUTE//2, 0, 5, self.hauteur))
        for i in range(0, self.hauteur, 60):
            if not (centre_y_b - LARGEUR_ROUTE//2 < i < centre_y_b + LARGEUR_ROUTE//2):
                pygame.draw.rect(surface, BLANC, (self.centre_x - 4, i, 8, 35))
       
        # Intersection
        pygame.draw.rect(surface, (55, 62, 68),
                         (self.centre_x - LARGEUR_ROUTE//2, self.centre_y - LARGEUR_ROUTE//2,
                          LARGEUR_ROUTE, LARGEUR_ROUTE))
   
    def dessiner_feux(self, surface):
        # Feu Voie A : abaissé davantage
        if self.images.get(self.couleur_feu_a):
            surface.blit(self.images[self.couleur_feu_a], self.pos_feu_a)
        else:
            couleur = {'green': (0,255,0), 'orange': (255,165,0), 'red': (255,0,0)}[self.couleur_feu_a]
            pygame.draw.circle(surface, couleur,
                               (self.pos_feu_a[0] + TAILLE_FEU//2, self.pos_feu_a[1] + TAILLE_FEU//2),
                               TAILLE_FEU//2)
       
        font = pygame.font.Font(None, 30)
        label_a = font.render("Voie A", True, NOIR)
        surface.blit(label_a, (self.pos_feu_a[0] + TAILLE_FEU//2 - label_a.get_width()//2,
                               self.pos_feu_a[1] - 25))  # abaissé de -50 → -70
       
        # Feu Voie B (inchangé)
        if self.images.get(self.couleur_feu_b):
            surface.blit(self.images[self.couleur_feu_b], self.pos_feu_b)
        else:
            couleur = {'green': (0,255,0), 'orange': (255,165,0), 'red': (255,0,0)}[self.couleur_feu_b]
            pygame.draw.circle(surface, couleur,
                               (self.pos_feu_b[0] + TAILLE_FEU//2, self.pos_feu_b[1] + TAILLE_FEU//2),
                               TAILLE_FEU//2)
       
        label_b = font.render("Voie B", True, NOIR)
        surface.blit(label_b, (self.pos_feu_b[0] + TAILLE_FEU//2 - label_b.get_width()//2,
                               self.pos_feu_b[1] - 25))
    def dessiner_voitures(self, surface):
        for voiture in self.voitures_a:
            if voiture.image:
                surface.blit(voiture.image, (voiture.x, voiture.y))
            else:
                dessiner_voiture_fallback(surface, voiture.x, voiture.y,
                                          TAILLE_VOITURE, int(TAILLE_VOITURE * 1.2),
                                          voiture.couleur_fallback)
       
        for voiture in self.voitures_b:
            if voiture.image:
                surface.blit(voiture.image, (voiture.x, voiture.y))
            else:
                dessiner_voiture_fallback(surface, voiture.x, voiture.y,
                                          int(TAILLE_VOITURE * 1.2), TAILLE_VOITURE,
                                          voiture.couleur_fallback)
   
    def dessiner_stats_avancees(self, surface, temps_simulation):
        x = self.largeur - 187
        y = 20
        w = 187
        h = self.hauteur - 40 // 1.5  # Adjusted for 1.5x smaller
        
        pygame.draw.rect(surface, (200, 200, 200), (x + 5, y + 5, w, h), border_radius=8)
        pygame.draw.rect(surface, BLANC, (x, y, w, h), border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), (x, y, w, h), 2, border_radius=8)
       
        font_titre = pygame.font.Font(None, 21)
        font_stats = pygame.font.Font(None, 15)
       
        titre = font_titre.render("STATISTIQUES", True, NOIR)
        surface.blit(titre, (x + 27, y + 7))
       
        y_pos = y + 40
       
        textes = [
            f"Temps: {temps_simulation:.1f}s",
            f"Total: {self.stats['total_vehicules']}",
            "",
            "VOIE A",
            f"Attente: {self.stats['voie_a_attente']}",
            f"Servis: {self.stats['voie_a_servis']}",
            f"Moy: {self.stats['temps_attente_a']:.1f}s",
            f"Débit: {self.stats['debit_a']:.1f}/min",
            "",
            "VOIE B",
            f"Attente: {self.stats['voie_b_attente']}",
            f"Servis: {self.stats['voie_b_servis']}",
            f"Moy: {self.stats['temps_attente_b']:.1f}s",
            f"Débit: {self.stats['debit_b']:.1f}/min"
        ]
       
        for texte in textes:
            if texte == "":
                y_pos += 10
            else:
                couleur = VERT_STATS if "Servis" in texte else NOIR
                t = font_stats.render(texte, True, couleur)
                surface.blit(t, (x + 15, y_pos))
                y_pos += 28
   
    def ajouter_voiture_a(self, vehicule: Vehicule):
        nb_attente = len([v for v in self.voitures_a if v.en_attente])
        x = self.centre_x - DISTANCE_DEPART_FILE - (nb_attente * ESPACEMENT_VOITURE)
        y = self.centre_y - TAILLE_VOITURE // 2
       
        idx = random.randint(1, 5)
        img_base = self.images.get(f'car{idx}')
        img_tournee = pygame.transform.rotate(img_base, -90) if img_base else None
       
        couleurs = [BLEU, (100, 150, 255), (0, 100, 200), (50, 180, 220), (30, 120, 180)]
       
        voiture = VoitureGraphique(vehicule, x, y, img_tournee, couleurs[idx-1], 'horizontale', True)
        self.voitures_a.append(voiture)
        self.stats['total_vehicules'] += 1
   
    def ajouter_voiture_b(self, vehicule: Vehicule):
        nb_attente = len([v for v in self.voitures_b if v.en_attente])
        x = self.centre_x - TAILLE_VOITURE // 2
        y = self.centre_y - DISTANCE_DEPART_FILE - (nb_attente * ESPACEMENT_VOITURE)
       
        idx = random.randint(1, 5)
        img_base = self.images.get(f'car{idx}')
        img_tournee = img_base
       
        couleurs = [ORANGE, (255, 150, 100), (255, 100, 50), (230, 140, 90), (200, 100, 60)]
       
        voiture = VoitureGraphique(vehicule, x, y, img_tournee, couleurs[idx-1], 'verticale', True)
        self.voitures_b.append(voiture)
        self.stats['total_vehicules'] += 1
   
    def faire_passer_voiture_a(self):
        for voiture in self.voitures_a:
            if voiture.en_attente:
                voiture.en_attente = False
                self.reorganiser_file_a()
                return voiture
        return None
   
    def faire_passer_voiture_b(self):
        for voiture in self.voitures_b:
            if voiture.en_attente:
                voiture.en_attente = False
                self.reorganiser_file_b()
                return voiture
        return None
   
    def reorganiser_file_a(self):
        voitures_attente = [v for v in self.voitures_a if v.en_attente]
        for i, v in enumerate(voitures_attente):
            v.x = self.centre_x - DISTANCE_DEPART_FILE - (i * ESPACEMENT_VOITURE)
            v.y = self.centre_y - TAILLE_VOITURE // 2
   
    def reorganiser_file_b(self):
        voitures_attente = [v for v in self.voitures_b if v.en_attente]
        for i, v in enumerate(voitures_attente):
            v.x = self.centre_x - TAILLE_VOITURE // 2
            v.y = self.centre_y - DISTANCE_DEPART_FILE - (i * ESPACEMENT_VOITURE)
   
    def animer_voitures(self):
        for voiture in self.voitures_a[:]:
            if not voiture.en_attente:
                voiture.x += 6
                if voiture.x > self.largeur + 100:
                    self.voitures_a.remove(voiture)
       
        for voiture in self.voitures_b[:]:
            if not voiture.en_attente:
                voiture.y += 6
                if voiture.y > self.hauteur + 100:
                    self.voitures_b.remove(voiture)
   
    def mettre_a_jour_debit(self, temps_actuel):
        if temps_actuel - self.dernier_temps_stats >= 3:
            if temps_actuel > 0:
                self.stats['debit_a'] = (self.stats['voie_a_servis'] / temps_actuel) * 60
                self.stats['debit_b'] = (self.stats['voie_b_servis'] / temps_actuel) * 60
                self.stats['historique_a'].append(self.stats['voie_a_attente'])
                self.stats['historique_b'].append(self.stats['voie_b_attente'])
                if len(self.stats['historique_a']) > 30:
                    self.stats['historique_a'].pop(0)
                    self.stats['historique_b'].pop(0)
            self.dernier_temps_stats = temps_actuel

class GestionnaireSimulation:
    def __init__(self, carrefour):
        self.carrefour = carrefour
        self.env = None
        self.evenements = Queue()
        self.thread = None
        self.actif = False
        self.voie_a = None
        self.voie_b = None
   
    def demarrer(self, lambda_a, lambda_b, config):
        self.actif = True
        self.thread = threading.Thread(target=self._executer, args=(lambda_a, lambda_b, config), daemon=True)
        self.thread.start()
   
    def _executer(self, lambda_a, lambda_b, config):
        self.env = simpy.Environment()
        self.voie_a = simpy.Resource(self.env, capacity=1)
        self.voie_b = simpy.Resource(self.env, capacity=1)
       
        systeme_feux = SystemeFeux(self.env, config)
        generateur = GenerateurVehicules(self.env, lambda_a, lambda_b)
       
        self.env.process(self._gerer_feux(config))
        self.env.process(self._generer_a(generateur))
        self.env.process(self._generer_b(generateur))
       
        while self.actif:
            self.env.run(until=self.env.now + 0.1)
            time.sleep(0.03)
   
    def _gerer_feux(self, config):
        while True:
            self.evenements.put(('feu_a', 'green'))
            self.evenements.put(('feu_b', 'red'))
            yield self.env.timeout(config.duree_vert_a)
            self.evenements.put(('feu_a', 'orange'))
            yield self.env.timeout(config.duree_jaune)
            self.evenements.put(('feu_a', 'red'))
            self.evenements.put(('feu_b', 'green'))
            yield self.env.timeout(config.duree_vert_b)
            self.evenements.put(('feu_b', 'orange'))
            yield self.env.timeout(config.duree_jaune)
            self.evenements.put(('feu_b', 'red'))
            yield self.env.timeout(config.duree_pietons)
   
    def _generer_a(self, gen):
        compteur = 0
        while True:
            yield self.env.timeout(gen.temps_inter_arrivee(gen.lambda_a))
            compteur += 1
            v = Vehicule(compteur, Direction.VOIE_A, self.env.now)
            self.evenements.put(('nouvelle_a', v))
            self.env.process(self._attendre_et_passer_a(v))
   
    def _attendre_et_passer_a(self, v):
        while self.carrefour.couleur_feu_a != 'green':
            yield self.env.timeout(0.1)
        with self.voie_a.request() as req:
            yield req
            self.evenements.put(('passer_a', v))
            yield self.env.timeout(0.1)
            v.temps_depart = self.env.now
            v.temps_attente = v.temps_depart - v.temps_arrivee
            self.evenements.put(('stats_a', v.temps_attente))
   
    def _generer_b(self, gen):
        compteur = 0
        while True:
            yield self.env.timeout(gen.temps_inter_arrivee(gen.lambda_b))
            compteur += 1
            v = Vehicule(compteur, Direction.VOIE_B, self.env.now)
            self.evenements.put(('nouvelle_b', v))
            self.env.process(self._attendre_et_passer_b(v))
   
    def _attendre_et_passer_b(self, v):
        while self.carrefour.couleur_feu_b != 'green':
            yield self.env.timeout(0.1)
        with self.voie_b.request() as req:
            yield req
            self.evenements.put(('passer_b', v))
            yield self.env.timeout(0.1)
            v.temps_depart = self.env.now
            v.temps_attente = v.temps_depart - v.temps_arrivee
            self.evenements.put(('stats_b', v.temps_attente))
   
    def traiter_evenements(self):
        while not self.evenements.empty():
            evt = self.evenements.get()
            t = evt[0]
            if t == 'feu_a': self.carrefour.couleur_feu_a = evt[1]
            elif t == 'feu_b': self.carrefour.couleur_feu_b = evt[1]
            elif t == 'nouvelle_a':
                self.carrefour.ajouter_voiture_a(evt[1])
                self.carrefour.stats['voie_a_attente'] += 1
            elif t == 'nouvelle_b':
                self.carrefour.ajouter_voiture_b(evt[1])
                self.carrefour.stats['voie_b_attente'] += 1
            elif t == 'passer_a':
                self.carrefour.faire_passer_voiture_a()
                self.carrefour.stats['voie_a_attente'] = max(0, self.carrefour.stats['voie_a_attente'] - 1)
                self.carrefour.stats['voie_a_servis'] += 1
            elif t == 'passer_b':
                self.carrefour.faire_passer_voiture_b()
                self.carrefour.stats['voie_b_attente'] = max(0, self.carrefour.stats['voie_b_attente'] - 1)
                self.carrefour.stats['voie_b_servis'] += 1
            elif t == 'stats_a':
                temps = evt[1]
                n = self.carrefour.stats['voie_a_servis']
                if n > 0:
                    moy = self.carrefour.stats['temps_attente_a']
                    self.carrefour.stats['temps_attente_a'] = (moy * (n-1) + temps) / n
            elif t == 'stats_b':
                temps = evt[1]
                n = self.carrefour.stats['voie_b_servis']
                if n > 0:
                    moy = self.carrefour.stats['temps_attente_b']
                    self.carrefour.stats['temps_attente_b'] = (moy * (n-1) + temps) / n
   
    def arreter(self):
        self.actif = False

# ========== ÉCRAN DE SÉLECTION ==========
def ecran_selection():
    pygame.init()
    screen = pygame.display.set_mode((FENETRE_LARGEUR, FENETRE_HAUTEUR))
    pygame.display.set_caption("Sélection du Scénario")
   
    font_titre = pygame.font.Font(None, 48)
    font_btn = pygame.font.Font(None, 32)
   
    scenarios = [
        {"nom": "Scénario 1 : Trafic Léger", "lambda": 0.3, "T_A": 30, "T_B": 25},
        {"nom": "Scénario 2 : Trafic Asymétrique", "lambda": 0.4, "T_A": 40, "T_B": 20},
        {"nom": "Scénario 3 : Optimisé", "lambda": 0.3, "T_A": 28, "T_B": 28}
    ]
   
    boutons = [pygame.Rect(100, 150 + i*120, 700, 80) for i in range(len(scenarios))]
   
    running = True
    while running:
        screen.fill(FOND)
        titre = font_titre.render("Choisissez un scénario", True, NOIR)
        screen.blit(titre, (FENETRE_LARGEUR//2 - titre.get_width()//2, 50))
       
        mouse_pos = pygame.mouse.get_pos()
        for rect, sc in zip(boutons, scenarios):
            couleur = BLEU if rect.collidepoint(mouse_pos) else (120, 120, 120)
            pygame.draw.rect(screen, (200, 200, 200), (rect.x + 5, rect.y + 5, rect.width, rect.height), border_radius=12)
            pygame.draw.rect(screen, couleur, rect, border_radius=12)
            pygame.draw.rect(screen, NOIR, rect, 3, border_radius=12)
            texte = font_btn.render(sc["nom"], True, BLANC)
            screen.blit(texte, texte.get_rect(center=rect.center))
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, sc in zip(boutons, scenarios):
                    if rect.collidepoint(event.pos):
                        pygame.quit()  # Fermer l'écran de sélection
                        return sc
       
        pygame.display.flip()

# ========== MAIN ==========
def main():
    scenario = ecran_selection()
    if not scenario:
        sys.exit()
   
    config = ConfigurationFeux(duree_vert_a=scenario["T_A"], duree_vert_b=scenario["T_B"])
   
    pygame.init()
    screen = pygame.display.set_mode((FENETRE_LARGEUR, FENETRE_HAUTEUR))
    pygame.display.set_caption(f"{scenario['nom']}")
    clock = pygame.time.Clock()
   
    print("\nChargement des images...")
    images = charger_images()
    print("Images chargées !\n")
   
    carrefour = CarrefourGraphique(FENETRE_LARGEUR, FENETRE_HAUTEUR, images)
    gestionnaire = GestionnaireSimulation(carrefour)
    gestionnaire.demarrer(scenario["lambda"], scenario["lambda"], config)
   
    font_info = pygame.font.Font(None, 24)
   
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
       
        gestionnaire.traiter_evenements()
        carrefour.animer_voitures()
        if gestionnaire.env:
            carrefour.mettre_a_jour_debit(gestionnaire.env.now)
       
        screen.fill(FOND)
        carrefour.dessiner_routes(screen)
        carrefour.dessiner_feux(screen)
        carrefour.dessiner_voitures(screen)
        if gestionnaire.env:
            carrefour.dessiner_stats_avancees(screen, gestionnaire.env.now)
       
        info = font_info.render("Appuyez sur ÉCHAP pour quitter", True, (100, 100, 100))
        screen.blit(info, (20, FENETRE_HAUTEUR - 30))
       
        pygame.display.flip()
        clock.tick(60)
   
    gestionnaire.arreter()
    pygame.quit()
    print("\nSimulation terminée !\n")

if __name__ == "__main__":
    main()